import json
import PyPDF2
import os
import re

import requests
from bs4 import BeautifulSoup
#import time
import argparse
import threading

def extract_lines_from(filename):
    try:
        with open(f"../data/{filename}", 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            text = ''.join(page.extract_text() for page in pdf.pages)
            return text
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

def create_blocks(text, block_length = 1024):
    i = 0
    f = []
    while(i < len(text)):
        line = text[i:i+block_length]
        for ii in range(len(line)):
            if line[len(line)-1 - ii] == '.' or line[len(line)-1 - ii] == ' ':
                f.append(line[:len(line)-1 - ii])
                i = i - ii
                break
        i += block_length
    return f

def extract_lines_in_1024_format_from(filename):
    try:
        with open(f"../data/{filename}", 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            lines = []
            for page in pdf.pages:
                if len(page.extract_text()) <= 1024:
                    lines.append(page.extract_text())
                else:
                    line = create_blocks(page.extract_text())
                    lines.extend(line)
            return lines
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

def extract_pages_from(filename):
    try:
        with open(f"../data/{filename}", 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            pages = []
            for page in pdf.pages:
                pages.append(page.extract_text())
            return pages
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None

def clean_text(json_text):
    cleaned_text = []
    replacements = {
        '\u00A0': ' ',
        '\u202F': ' ',
        '\u00a9': "'",
        '\u02bb': "'",
        '\u02bc': "'",
        '\u2019': "'",
        '\u2014': '-',
        '\u2013': '-',
        '\u25a0': '-',
        '\u2022': '-',
        '\u201d': '"',
        '\u201c': '"',
        '\u00b0': '°',
        '\u00ba': '°'
    }

    for text in json_text:
        for old, new in replacements.items():
            text = text.replace(old, new)  

        text = re.sub(r'[\n\t\r]', ' ', text) # replace other chars with space
        text = re.sub(r'\s+', ' ', text).strip() # reduce multiple spaces to single one
        cleaned_text.append(text)
    return cleaned_text

def process_pdf(filename, lines) -> bool:
    if lines:
        array_data = extract_lines_in_1024_format_from(filename)
    else:
        array_data = extract_pages_from(filename)
        
    array_data = clean_text(array_data)
    error = False
    # save data as json
    try:
        with open(f"../formatted_data/{filename.replace('.pdf', '_formatted.json')}", 'w') as outfile:
            json.dump(array_data, outfile, indent=2)
    except IOError as e:
        print(f"Error saving result of {filename}: {e}")
        error = True
    
    return False if error else True

def process_data(lines):
    for filename in os.listdir("../data/"):
        if not filename.endswith(".pdf"):
            continue
        if process_pdf(filename, lines):
            print(f"{filename} processed.")
        else:
            print(f"{filename} failed.")

def delete(dir):
    for filename in os.listdir(f"../{dir}/"):
        try:
            os.remove(f"../{dir}/{filename}")
        except OSError as e:
            print(f"Error while removing file of {filename}: {e}")
            return False

def get_data():
    response = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
    soup = BeautifulSoup(response.content, "html.parser") 
    return soup.find("tbody")

def parse_companies(entire_table):
    companies = []
    for table_row in entire_table.findAll("tr")[1:]: 
        columns = table_row.findAll("td")
        company = columns[0].get_text(strip=True)
        companies.append(company)
    return companies

def download_company_report(company):
    try:
        # Send request to get the next HTML of the company to get the needed URL "extension" (example: to add /Company/apple-inc to https://www.responsibilityreports.com)
        r = requests.get(f"https://www.responsibilityreports.com/Companies?search={company}")
        soup = BeautifulSoup(r.text, "html.parser")
        all_links = soup.findAll("a")

        company_link = None
        for a in all_links:
            if a.get("href", "").startswith("/Company"):
                company_link = a["href"]
                break

        if not company_link:
            print(f"No company link found for {company}")
            return

        r = requests.get(f"https://www.responsibilityreports.com{company_link}")
        soup = BeautifulSoup(r.text, "html.parser")
        all_links = soup.findAll("a")

        download_url = None
        for a in all_links:
            if a.get("href", "").startswith("/HostedData/") and a.text == "Download":
                download_url = a["href"]
                break

        if not download_url:
            print(f"No download URL found for {company}")
            return

        filename = download_url[42:]  # Extract filename from URL
        print(f"Getting file from URL: https://www.responsibilityreports.com{download_url}")

        r = requests.get(f"https://www.responsibilityreports.com{download_url}")
        if r.status_code == 200:
            # Adjust "Downloads" directory appropriately
            download_path = os.path.abspath(os.getcwd())[:-3] + "data"
            download_path = os.path.join(download_path, filename)

            # Save the PDF file
            with open(download_path, 'wb') as f:
                f.write(r.content)

            print(f"Successfully downloaded: {filename}\n")
        else:
            print(f"Failed to download file for {company}, status code: {r.status_code}")

    except Exception as exception:
        print(f"Error downloading report for {company}: {exception}")

def download_reports(companies):
    threads = []

    for company in companies:
        # Create a thread for each company
        thread = threading.Thread(target=download_company_report, args=(company,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

def scrape():
    data = get_data()
    companies = parse_companies(data)
    download_reports(companies)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Asymmetric encryption and decryption")
    parser.add_argument("-s", "--scrape", action="store_true", help="Get sustainbility reports from https://www.responsibilityreports.com")
    parser.add_argument("-l", "--lines", action="store_true", help="Process report line by line")
    parser.add_argument("-p", "--pages", action="store_true", help="Process report by pages of the document") #type=str
    parser.add_argument("-c", "--clearjson", action="store_true", help="Use to remove all saved formatted json files")
    parser.add_argument("-d", "--deletedocuments", action="store_true", help="Use to remove all saved sustainability reports")
    
    args = parser.parse_args()

    if args.scrape:
        scrape()

    if args.lines:
        process_data(args.lines)
    elif args.pages:
        process_data(False)

    if args.clearjson:
        delete("formatted_data")
    elif args.deletedocuments:
        delete("data")
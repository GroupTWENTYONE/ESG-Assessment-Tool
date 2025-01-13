import json
import PyPDF2
import os
import re

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
#import time
import argparse

def extract_lines_from(filename):
    try:
        with open(f"../data/{filename}", 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            text = ''.join(page.extract_text() for page in pdf.pages)
            return text
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None
'''
def create_blocks(text, block_length = 1024):
    i=0
    f=[]
    while(i<len(text)):
        f.append(text[i:i+block_length])
        i+=block_length
    return f
'''
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
            print(f"{filename} processed")
        else:
            print(f"{filename} failed")


def delete(dir):
    for filename in os.listdir(f"../{dir}/"):
        try:
            os.remove(f"../{dir}/{filename}")
        except OSError as e:
            print(f"Error removing file of {filename}: {e}")
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

def setup_driver():
    download_directory_path = os.path.abspath(os.getcwd())[:-3] + "data"

    ChromeDriverManager().install()
    chrome_download_configs = {
        "download.default_directory": download_directory_path,
        "download.prompt_for_download": False, 
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True
    }
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option('prefs', chrome_download_configs)
    return webdriver.Chrome(options=chrome_options)

def download_reports(companies, driver):
    wait = WebDriverWait(driver, 1)

    counter = 1 # <- TEST
    for company in companies:
        if counter >= 8: break # <- TEST
        try:
            driver.get("https://www.responsibilityreports.com")

            search_bar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.container > section.banner_section > div > div > div.left_section > form > input[type=text]:nth-child(2)")))
            search_bar.send_keys(company) # here the element of the company list but you can use for example "AAPL" as well
            search_bar.submit()

            link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.container > section.category_section > div.apparel_stores_company_list > ul > li:nth-child(2) > span:nth-child(1) > a")))
            link.click()

            try:
                first_report = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "body > div.container > section > div.profile_content_block > div.right_section > div.most_recent_block > div.most_recent_content_block > div.view_btn > a")))
                first_report.click()

                try:
                    popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "body > div.container > div > div > div.close_popup > a")))
                    popup.click()
                except:
                    pass
            except Exception as excetpion:
                pass

        except Exception as exception:
            print(f"{exception}")
            continue

        counter += 1 # <- TEST

def scrape():
    data = get_data()
    companies = parse_companies(data)
    driver = setup_driver()
    download_reports(companies, driver)
    driver.quit()

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

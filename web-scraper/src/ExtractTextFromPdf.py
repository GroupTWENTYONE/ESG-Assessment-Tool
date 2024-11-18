import json
import PyPDF2
import os

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time

def extract_text_from(filename):

    try:
        with open(f"../data/{filename}", 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            text = ''.join(page.extract_text() for page in pdf.pages)
            return text
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None
    
def to_string_array(text):

    data = text.split(". ")
    '''
    for line in data:
        print("\nTHIS IS A SINGLE LINE: --------------------------------")
        print(line)
        print("\n")
    '''
    return data
    
def process_pdf(filename) -> bool:
    # extract text 
    extracted_text = extract_text_from(filename)
    
    # transform into output format
    array_data = to_string_array(extracted_text)

    error = False

    #json_data = {line for line in array_data}
    # save 
    try:
        with open(f"../formatted_data/{filename.replace('.pdf', '_formatted.json')}", 'w',encoding='utf-8') as outfile:
            json.dump(array_data, outfile, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error saving result of {filename}: {e}")
        error = True
    
    #remove pdf
    '''
    try:
        os.remove(f"../data/{filename}")
    except OSError as e:
        print(f"Error removing pdf of {filename}: {e}")
        error = True
    '''
    
    return False if error else True

def process_data():
    #filenames = ["NASDAQ_AAPL_2022.pdf"]

    for filename in os.listdir("../data/"):
        if not filename.endswith(".pdf"):
            continue
        if process_pdf(filename) :
            print(f"{filename} processed")
        else :
            print(f"{filename} failed")



def clear_cache():
    for filename in os.listdir("../formatted_data/"):
        try:
            os.remove(f"../formatted_data/{filename}")
        except OSError as e:
            print(f"Error removing pdf of {filename}: {e}")
            return False
    

#clear_cache()

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

    counter = 1
    for company in companies:
        if counter >= 9: break
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

        counter += 1

def scrape():
    data = get_data()
    companies = parse_companies(data)

    driver = setup_driver()
    download_reports(companies, driver)

    driver.quit()

if __name__ == "__main__":
    scrape()
    process_data() # need to be adjusted to the webscraping process
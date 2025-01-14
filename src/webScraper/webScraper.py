import os
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

RESPONSIBILITY_REPORTS_URL = "https://www.responsibilityreports.com"
WIKI_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
DATA_DIR = "./raw_data/"

class WebScraper:
    @staticmethod
    def get_sp500_companies():
        """Scrapes the list of S&P 500 companies from Wikipedia."""
        response = requests.get(WIKI_SP500_URL)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("tbody")

        companies = []
        for row in table.find_all("tr")[1:]:
            columns = row.find_all("td")
            company = columns[0].get_text(strip=True)
            companies.append(company)

        return companies

    @staticmethod
    def setup_driver():
        """Sets up the Chrome WebDriver with necessary options."""
        download_directory_path = os.path.abspath(DATA_DIR)

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

    @staticmethod
    def download_reports(companies):
        """Downloads responsibility reports for the given companies."""
        driver = WebScraper.setup_driver()
        wait = WebDriverWait(driver, 10)

        for index, company in enumerate(companies, start=1):
            if index > 15:  # Limit for testing
                break

            try:
                driver.get(RESPONSIBILITY_REPORTS_URL)

                search_bar = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[type=text]:nth-child(2)")))
                search_bar.send_keys(company)
                search_bar.submit()

                link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "li:nth-child(2) > span:nth-child(1) > a")))
                link.click()

                try:
                    download_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.view_btn > a")))
                    download_button.click()

                    try:
                        popup = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.close_popup > a")))
                        popup.click()
                    except:
                        pass
                except Exception as e:
                    print(f"Download failed for {company}: {e}")

            except Exception as e:
                print(f"Error with {company}: {e}")
                continue

        driver.quit()
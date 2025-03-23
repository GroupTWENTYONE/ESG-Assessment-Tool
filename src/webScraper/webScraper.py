import os
import threading
import requests
from bs4 import BeautifulSoup

RESPONSIBILITY_REPORTS_URL = "https://www.responsibilityreports.com"
WIKI_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
DATA_DIR = "../raw_data/"

class WebScraper:    
    def get_data(self):
        response = requests.get("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        soup = BeautifulSoup(response.content, "html.parser") 
        return soup.find("tbody")

    def parse_companies(self, entire_table):
        companies = []
        for table_row in entire_table.findAll("tr")[1:]: 
            columns = table_row.findAll("td")
            company = columns[0].get_text(strip=True)
            companies.append(company)
        return companies

    def download_company_report(self, company):
        try:
            # send request to get the next HTML of the company to get the needed URL "extension" (example: to add /Company/apple-inc to https://www.responsibilityreports.com)
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

            filename = download_url[42:]  # extract filename from URL
            print(f"Getting file from URL: https://www.responsibilityreports.com{download_url}")

            r = requests.get(f"https://www.responsibilityreports.com{download_url}")
            if r.status_code == 200:
                # adjust "Downloads" directory appropriately
                download_path = os.path.abspath(DATA_DIR)
                download_path = os.path.join(download_path, filename)

                # save the PDF file
                with open(download_path, 'wb') as f:
                    f.write(r.content)

                print(f"Successfully downloaded: {filename}\n")
            else:
                print(f"Failed to download file for {company}, status code: {r.status_code}")

        except Exception as exception:
            print(f"Error downloading report for {company}: {exception}")

    def download_reports(self, companies):
        threads = []

        for company in companies:
            # create a thread for each company as this is not a cpu intensive task
            thread = threading.Thread(target=self.download_company_report, args=(company,))
            threads.append(thread)
            thread.start()

        # wait for all threads to finish
        for thread in threads:
            thread.join()

    def scrape(self):
        data = self.get_data()
        companies = self.parse_companies(data)
        self.download_reports(companies)
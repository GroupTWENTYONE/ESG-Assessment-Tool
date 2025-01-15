import os
from textAnalysis.textAnalysis import ESGAnalyzer
from databaseAccess.database import Database
from logger.logger import Logger

from webScraper.webScraper import WebScraper
from webScraper.documentProcessor import DocumentProcessor

base_path = "./prepared_data/"
res_path = "./res"
logger = Logger("main_program")

def main():

    run_web_scaper()

    analyzer = ESGAnalyzer()
    
    try:
        for file in os.listdir(base_path):
            filename = os.fsdecode(file)
            if not os.path.isdir(os.path.join(base_path, filename)):
                continue
            print(filename)
            analyzer.process_company(filename)
    except Exception as e:
        logger.log("error", f"Error processing company {filename}: {str(e)}")

def run_web_scaper():
    scraper = WebScraper()
    companies = scraper.get_sp500_companies()
    scraper.download_reports(companies)

    DocumentProcessor.process_all_pdfs(split_into_lines=True)

def print_database():
    database = Database()
    database.list_companies()

if __name__ == "__main__":
    main()
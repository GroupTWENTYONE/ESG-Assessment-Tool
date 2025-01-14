import os
from textAnalysis.textAnalysis import ESGAnalyzer
from databaseAccess.database import Database
from logger.logger import Logger

from webScraper.webScraper import WebScraper
from webScraper.documentProcessor import DocumentProcessor

base_path = "./res"
logger = Logger("main_program")

def main():

    analyzer = ESGAnalyzer()
    
    try:
        for file in os.listdir(base_path):
            filename = os.fsdecode(file)
            if os.path.isdir(os.path.join(base_path, filename)):
                continue
            print(filename)
            # analyzer.process_company("Adobe", "ADBE")
    except Exception as e:
        logger.log("error", f"Error processing company {filename}: {str(e)}")
    
    
    # for each company
    #   analyzer process_company

def web_scaper_test():
    scraper = WebScraper()
    companies = scraper.get_sp500_companies()
    scraper.download_reports(companies)

    DocumentProcessor.process_all_pdfs(split_into_lines=True)

def print_database():
    database = Database()
    database.list_companies()

if __name__ == "__main__":
    web_scaper_test()
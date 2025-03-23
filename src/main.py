from concurrent.futures import ThreadPoolExecutor
import os
import asyncio
import threading
from textAnalysis.textAnalysis import ESGAnalyzer
from databaseAccess.database import Database
from logger.logger import Logger

from webScraper.webScraper import WebScraper
from webScraper.documentProcessor import DocumentProcessor

import time

base_path = "../prepared_data/"

def main():
    start_time = time.time()
    run_web_scaper()
    analyze_and_store_companies()

    end_time = time.time()
    print(f"Total duration: {end_time - start_time:.2f} seconds.")

def run_web_scaper():
    scraper = WebScraper()
    scraper.scrape()

    DocumentProcessor.process_all_pdfs(split_into_lines=True)

def analyze_and_store_companies():
    logger = Logger("main_program")
    
    try:
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor: # as many threads as cpu cores available (does not create a thread for each file as this might be more cpu intensive and therefore less efficient)
            futures = []
            
            for file in os.listdir(base_path):
                filename = os.fsdecode(file)
                if not os.path.isdir(os.path.join(base_path, filename)):
                    continue

                analyzer = ESGAnalyzer()
                # starting the "threads"
                future = executor.submit(analyzer.process_company, filename)
                futures.append(future)
            
            # wait for all threads to finish
            for future in futures:
                future.result()

    except Exception as e:
        logger.log("error", f"Error processing company {filename}: {str(e)}")

def print_database():
    database = Database()
    database.list_companies()

if __name__ == "__main__":
    main()
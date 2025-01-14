import os
from textAnalysis.textAnalysis import ESGAnalyzer
from databaseAccess.database import Database
from logger.logger import Logger

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

def print_database():
    database = Database()
    database.list_companies()

if __name__ == "__main__":
    main()
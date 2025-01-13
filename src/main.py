from textAnalysis.textAnalysis import ESGAnalyzer
from databaseAccess.database import Database

def main():

    analyzer = ESGAnalyzer()
    
    analyzer.process_company("Adobe", "ADBE")
    
    # for each company
    #   analyzer process_company

def print_database():
    database = Database()
    database.list_companies()

if __name__ == "__main__":
    main()
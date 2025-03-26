from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib.parse

# Verbindung zur MongoDB herstellen
# More informations: https://pymongo.readthedocs.io/en/stable/examples/authentication.html
class Database:
    def __init__(self):
        self.username = urllib.parse.quote_plus('root') # Username from Dockerfile
        self.password = urllib.parse.quote_plus('example') # Password from Dockerfile
        self.client = MongoClient('mongodb://%s:%s@localhost:27017' % (self.username, self.password))

        self.db = self.client["company_db"]
        self.companies_collection = self.db["companies"]

    def add_company(self, name: str, ticker: str) -> str:
        """
        Function to add Company to collection
        """
        company = {
            "name": name,
            "ticker": ticker,
            "esg_components": {
                "E": [],
                "S": [],
                "G": []
            }
        }
        result = self.companies_collection.insert_one(company)
        print(f"Company inserted with ID: {result.inserted_id}")
        return result.inserted_id

    def add_esg_component(self, company_id: str, category: str, statement: str) -> int:
        """
        Add ESG-Component to Company

        :param company_id: ID of company as String
        :param category: Category of ESG (E, S, G)
        :param statement: Sentence
        """
        if category not in ["E", "S", "G"]:
            print("Invalid Category. Please use: E, S or G.")
            return

        result = self.companies_collection.update_one(
            {"_id": ObjectId(company_id)},
            {"$push": {f"esg_components.{category}": statement}}
        )

        if result.modified_count > 0:
            print("ESG-Component added successfully.")
            return 1
        else:
            print("Failure on insert of ESG-Component. Check Company-ID")
            return -1

    def get_company(self, company_id):
        """
        Get Company by Company ID

        :param company_id: ID of company (String)
        :return: Company as document
        """
        company = self.companies_collection.find_one({"_id": ObjectId(company_id)})
        if company:
            return company
        else:
            print("Company does not exist.")
            return None

    def list_companies(self):
        """
        Get every company
        """
        companies = self.companies_collection.find()
        for company in companies:
            print(company)


    def get_company_id_by_ticker(self, ticker) -> str | None:
        """
        get Company ID by Ticker

        :param ticker: Stockticker of company e.g. AMZN
        :return: Company ID or none
        """
        company = self.companies_collection.find_one({"ticker": ticker})
        if company:
            return str(company["_id"])
        else:
            print("Company does not exist")
            return None


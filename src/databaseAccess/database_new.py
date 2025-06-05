from pymongo import MongoClient
from bson.objectid import ObjectId
import urllib.parse
from typing import Optional

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
            },
            "calculated_esg_score": None,
            "spglobal_esg_score": None,
            "spglobal_individual_scores": {
                "environmental": None,
                "social": None,
                "governance": None
            }
        }
        result = self.companies_collection.insert_one(company)
        print(f"Company inserted with ID: {result.inserted_id}")
        return result.inserted_id

    def migrate_old_entries_to_new_schema(self):
        result = self.companies_collection.update_many(
            {},
            {
                "$set": {
                    "calculated_esg_score": None,
                    "spglobal_esg_score": None,
                    "spglobal_individual_scores": {
                        "environmental": None,
                        "social": None,
                        "governance": None
                    }
                }
            }
        )
        print(f"Modified {result.modified_count} existing companies.")

    def set_calculated_esg_score(self, company_id: str, score: int) -> int:
        """
        Set calculated_esg_score for a company, clearing any existing value first
        """
        # Clear existing calculated score if present
        existing = self.companies_collection.find_one({"_id": ObjectId(company_id)})
        if existing and existing.get("calculated_esg_score") is not None:
            self.companies_collection.update_one(
                {"_id": ObjectId(company_id)},
                {"$set": {"calculated_esg_score": None}}
            )

        result = self.companies_collection.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"calculated_esg_score": score}}
        )

        if result.modified_count > 0:
            print("calculated_esg_score updated successfully.")
            return 1
        else:
            print("Failed to update calculated_esg_score. Check Company-ID.")
            return -1
        

    def set_spglobal_esg_score(self, company_id: str, score: int) -> int:
        """
        Set spglobal_esg_score for a company, clearing any existing value first
        """
        # Clear existing SP Global ESG score if present
        existing = self.companies_collection.find_one({"_id": ObjectId(company_id)})
        if existing and existing.get("spglobal_esg_score") is not None:
            self.companies_collection.update_one(
                {"_id": ObjectId(company_id)},
                {"$set": {"spglobal_esg_score": None}}
            )

        result = self.companies_collection.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": {"spglobal_esg_score": score}}
        )

        if result.modified_count > 0:
            print("spglobal_esg_score updated successfully.")
            return 1
        else:
            print("Failed to update spglobal_esg_score. Check Company-ID.")
            return -1

    def set_spglobal_individual_scores(self, company_id: str, environmental: int = None, social: int = None, governance: int = None) -> int:
        """
        Set individual ESG scores for a company
        """
        update_data = {}
        if environmental is not None:
            update_data["spglobal_individual_scores.environmental"] = environmental
        if social is not None:
            update_data["spglobal_individual_scores.social"] = social
        if governance is not None:
            update_data["spglobal_individual_scores.governance"] = governance

        if not update_data:
            print("No scores provided to update.")
            return -1

        result = self.companies_collection.update_one(
            {"_id": ObjectId(company_id)},
            {"$set": update_data}
        )

        if result.modified_count > 0:
            print("Individual ESG scores updated successfully.")
            return 1
        else:
            print("Failed to update individual ESG scores. Check Company-ID.")
            return -1

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
        companies = self.companies_collection.find()
        return [company.get('name') for company in companies]

    def get_company_id_by_name(self, name) -> Optional[str]:
        company = self.companies_collection.find_one({"name": name})
        if company:
            return str(company["_id"])
        else:
            return None
    
    def get_company_id_by_ticker(self, ticker) -> Optional[str]:
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

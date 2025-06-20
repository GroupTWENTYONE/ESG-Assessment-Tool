import sys
import os

current_script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_script_dir)
sys.path.insert(0, parent_dir)

from databaseAccess.database import Database
from spglobalScraper import WebScraper

db = Database()

companies = db.list_companies()

scraper = WebScraper()            # no work done here
scraper.scrape(companies)   


# doesnt work currently i dont now hy, if you want to insert esg scores from spglobal you have to do it in the webscraper (spglobal)
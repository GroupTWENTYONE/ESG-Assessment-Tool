import os
import threading
import requests
import urllib.parse
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bs4 import BeautifulSoup
from logger.logger import Logger

SEARCH_URL = "https://www.spglobal.com/esg/csa/esg-proxy?comp-name="
COMPANY_URL = "https://www.spglobal.com/esg/scores/results?cid="

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))
DATA_DIR = os.path.join(BASE_DIR, "spg_global_data")
OUTPUT_FILE = os.path.join(DATA_DIR, "esg_scores.json")

class WebScraper:
    def __init__(self, company_names):
        self.logger = Logger("spglobal_scraper")
        self.company_scores = {}
        if not os.path.exists(DATA_DIR):
             try:
                 os.makedirs(DATA_DIR)
                 self.logger.log("info", f"Created directory: {DATA_DIR}")
             except OSError as e:
                 self.logger.log("error", f"Failed to create directory {DATA_DIR}: {e}")
                 raise

        self.process_companies(company_names)
        self.save_scores_to_json()

    def process_companies(self, company_names):
        """Iterates through company names, fetches and stores ESG scores."""
        for name in company_names:
            self.logger.log("info", f"Processing company: {name}")
            try:
                company_id = self.search_company(name)
                if company_id:
                    score = self.get_esg_score(company_id)
                    if score:
                        self.company_scores[name] = score
                        self.logger.log("info", f"Successfully retrieved score for {name}: {score}")
                    else:
                        self.logger.log("warning", f"Could not retrieve score for {name} (ID: {company_id})")
                else:
                     self.logger.log("warning", f"Could not find ID for company: {name}")
            except requests.exceptions.RequestException as e:
                self.logger.log("error", f"Network error processing {name}: {e}")
            except Exception as e:
                self.logger.log("error", f"An unexpected error occurred processing {name}: {e}")


    def search_company(self, company_name):
        """Searches for the company ID."""
        search_url_full = SEARCH_URL + urllib.parse.quote(company_name)
        self.logger.log("debug", f"Searching for company ID using URL: {search_url_full}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "X-NewRelic-ID": "VQ4AVldVDRABVVNXBgMPX1Y=",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Referer": "https://www.spglobal.com/esg/solutions/esg-scores-data",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            }
            response = requests.get(search_url_full, timeout=10, headers=headers)
            response.raise_for_status() 
            response_json = response.json() 

            if isinstance(response_json, list) and len(response_json) > 0:
                data_list = response_json
            elif isinstance(response_json, dict) and response_json.get("data") and isinstance(response_json["data"], list) and len(response_json["data"]) > 0:
                data_list = response_json["data"]
            else:
                self.logger.log("warning", f"No data found for company: {company_name} in response: {response_json}")
                return None
            # Extract company ID from first item
            company_id = data_list[0].get("id")
            if company_id:
                self.logger.log("debug", f"Found company ID for {company_name}: {company_id}")
                return company_id
            else:
                self.logger.log("warning", f"ID key missing in data for company: {company_name}. Response data: {response_json['data'][0]}")
                return None
        except requests.exceptions.Timeout:
            self.logger.log("error", f"Timeout occurred while searching for company {company_name} at {search_url_full}")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.log("error", f"HTTP error searching for company {company_name}: {e}. Status code: {response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.log("error", f"Network error searching for company {company_name}: {e}")
            return None
        except json.JSONDecodeError as e:
             self.logger.log("error", f"Error decoding JSON response for {company_name} from {search_url_full}: {e}. Response text: {response.text}")
             return None
        except IndexError:
             # This might happen if "data" is an empty list
             self.logger.log("error", f"Index error accessing data for {company_name}. Response JSON: {response_json}")
             return None
        except Exception as e:
             # Catch any other unexpected errors during search
             self.logger.log("error", f"An unexpected error occurred during search for {company_name}: {e}")
             return None


    def get_esg_score(self, company_id):
        """Retrieves the ESG score using the company ID."""
        company_url_full = COMPANY_URL + str(company_id)
        self.logger.log("debug", f"Fetching ESG score from URL: {company_url_full}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
                "Accept": "application/json, text/javascript, */*; q=0.01",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "X-NewRelic-ID": "VQ4AVldVDRABVVNXBgMPX1Y=",
                "X-Requested-With": "XMLHttpRequest",
                "Sec-GPC": "1",
                "Connection": "keep-alive",
                "Referer": "https://www.spglobal.com/esg/solutions/esg-scores-data",
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "TE": "trailers"
            }
            response = requests.get(company_url_full, headers=headers,timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            score_element = soup.select_one(".score-module .score-value")
            if not score_element:
                 score_element = soup.select_one(".scoreModule__score") 

            if score_element:
                score = score_element.get_text(strip=True)
                self.logger.log("debug", f"Found score element for ID {company_id}. Score: {score}")
                return score
            else:
                self.logger.log("warning", f"Score element not found using selectors for company ID: {company_id} on page {company_url_full}")
                return None
        except requests.exceptions.Timeout:
            self.logger.log("error", f"Timeout occurred while fetching score page for ID {company_id} at {company_url_full}")
            return None
        except requests.exceptions.HTTPError as e:
            self.logger.log("error", f"HTTP error fetching score page for ID {company_id}: {e}. Status code: {response.status_code}")
            return None
        except requests.exceptions.RequestException as e:
            self.logger.log("error", f"Network error fetching score page for ID {company_id}: {e}")
            return None
        except Exception as e:
            self.logger.log("error", f"Error parsing score page HTML for ID {company_id}: {e}")
            return None

    def save_scores_to_json(self):
        """Saves the collected scores to a JSON file."""
        self.logger.log("info", f"Attempting to save {len(self.company_scores)} scores to {OUTPUT_FILE}")
        try:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.company_scores, f, ensure_ascii=False, indent=4)
            self.logger.log("info", f"Successfully saved scores to {OUTPUT_FILE}")
        except IOError as e:
            self.logger.log("error", f"Error saving scores to JSON file {OUTPUT_FILE}: {e}")
        except TypeError as e:
            self.logger.log("error", f"Data type error while preparing scores for JSON saving: {e}. Data: {self.company_scores}")
        except Exception as e:
            self.logger.log("error", f"An unexpected error occurred during JSON saving: {e}")

if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    main_logger = Logger("__main__") 
    main_logger.log("info", "Starting S&P Global ESG score scraping...")

    companies_to_scrape = ["Apple Inc."] # Example list
    try:
        scraper = WebScraper(companies_to_scrape)
        main_logger.log("info", "Scraping process completed.")
        main_logger.log("info", f"Collected Scores ({len(scraper.company_scores)}):")
        main_logger.log("info", json.dumps(scraper.company_scores, indent=4))
        main_logger.log("info", f"Check the log file at ./logs/spglobal_scraper.log and the output file at {OUTPUT_FILE}")
    except Exception as e:
        main_logger.log("critical", f"A critical error occurred during the scraping process: {e}")

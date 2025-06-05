import os
import threading
import requests
import urllib.parse
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from bs4 import BeautifulSoup
from logger.logger import Logger
from databaseAccess.database import Database

SEARCH_URL = "https://www.spglobal.com/esg/csa/esg-proxy?comp-name="
COMPANY_URL = "https://www.spglobal.com/esg/scores/results?cid="

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))
DATA_DIR = os.path.join(BASE_DIR, "spg_global_data")
OUTPUT_FILE = os.path.join(DATA_DIR, "esg_scores.json")

class WebScraper:
    def __init__(self, company_names=None):
        self.logger = Logger("spglobal_scraper")
        self.company_scores = {}
        if not os.path.exists(DATA_DIR):
             try:
                 os.makedirs(DATA_DIR)
                 self.logger.log("info", f"Created directory: {DATA_DIR}")
             except OSError as e:
                 self.logger.log("error", f"Failed to create directory {DATA_DIR}: {e}")
                 raise      
        if company_names is not None:
            self.scrape(company_names)

    def scrape(self, company_names):
        """Run scraping for given list of company names."""
        self.process_companies(company_names)
        self.save_scores_to_json()

    def process_companies(self, company_names):
        """Iterates through company names, fetches and stores ESG scores."""
        db = Database()
        for name in company_names:
            self.logger.log("info", f"Processing company: {name}")
            try:
                company_id = self.search_company(name)
                if company_id:
                    score_data = self.get_esg_score(company_id)
                    if score_data:
                        overall_score = score_data.get("overall_score")
                        individual_scores = score_data.get("individual_scores", {})
                        
                        # Store overall score if available
                        if overall_score:
                            self.company_scores[name] = overall_score
                            db_id = db.get_company_id_by_name(name)
                            if db_id:
                                db.set_spglobal_esg_score(db_id, overall_score)
                                self.logger.log("info", f"Successfully stored overall score for {name}: {overall_score}")
                        
                        # Store individual scores if available
                        if any(individual_scores.values()):
                            db_id = db.get_company_id_by_name(name)
                            if db_id:
                                db.set_spglobal_individual_scores(
                                    db_id,
                                    environmental=individual_scores.get("environmental"),
                                    social=individual_scores.get("social"),
                                    governance=individual_scores.get("governance")
                                )
                                self.logger.log("info", f"Successfully stored individual scores for {name}: E:{individual_scores.get('environmental')}, S:{individual_scores.get('social')}, G:{individual_scores.get('governance')}")
                        
                        if not overall_score and not any(individual_scores.values()):
                            self.logger.log("warning", f"No scores found for {name} (ID: {company_id})")
                    else:
                        self.logger.log("warning", f"Could not retrieve score data for {name} (ID: {company_id})")
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
            
            overall_score = None
            if score_element:
                overall_score = score_element.get_text(strip=True)
                self.logger.log("debug", f"Found overall score element for ID {company_id}. Score: {overall_score}")
            
            # Try to get individual ESG scores
            individual_scores = self.get_individual_esg_scores(soup, company_id)
            
            # Return both overall and individual scores
            result = {
                "overall_score": overall_score,
                "individual_scores": individual_scores
            }
            
            if overall_score or any(individual_scores.values()):
                return result
            else:
                self.logger.log("warning", f"No scores found for company ID: {company_id} on page {company_url_full}")
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
        
    def get_individual_esg_scores(self, soup, company_id):
        """Extract individual E, S, G scores from the webpage with improved methods."""
        individual_scores = {
            "environmental": None,
            "social": None,
            "governance": None
        }
        
        try:
            # Method 1: Look for specific data-score attributes in dimension divs
            self.logger.log("debug", "Trying data-score attribute method for individual scores")
            
            # Environmental score
            env_div = soup.find("div", id="dimentions-score-env")
            if env_div and env_div.get("data-score"):
                try:
                    individual_scores["environmental"] = int(env_div.get("data-score"))
                    self.logger.log("debug", f"Found Environmental score via data-score: {individual_scores['environmental']}")
                except ValueError:
                    self.logger.log("warning", f"Could not parse Environmental data-score: {env_div.get('data-score')}")
            
            # Social score
            social_div = soup.find("div", id="dimentions-score-social")
            if social_div and social_div.get("data-score"):
                try:
                    individual_scores["social"] = int(social_div.get("data-score"))
                    self.logger.log("debug", f"Found Social score via data-score: {individual_scores['social']}")
                except ValueError:
                    self.logger.log("warning", f"Could not parse Social data-score: {social_div.get('data-score')}")
            
            # Governance score
            gov_div = soup.find("div", id="dimentions-score-govecon")
            if gov_div and gov_div.get("data-score"):
                try:
                    individual_scores["governance"] = int(gov_div.get("data-score"))
                    self.logger.log("debug", f"Found Governance score via data-score: {individual_scores['governance']}")
                except ValueError:
                    self.logger.log("warning", f"Could not parse Governance data-score: {gov_div.get('data-score')}")

            # If we found all scores via the primary method, return them
            if all(individual_scores.values()):
                self.logger.log("debug", f"Successfully found all individual scores via data-score method: {individual_scores}")
                return individual_scores

            # Method 2: Look for DimensionScore__label sections (fallback)
            dimension_labels = soup.select(".DimensionScore__label ul")
            
            for ul in dimension_labels:
                # Get the first li element which should contain the company's score
                first_li = ul.select_one("li")
                if first_li:
                    span = first_li.select_one("span")
                    if span:
                        score_text = span.get_text(strip=True)
                        try:
                            score = int(score_text)
                            
                            # Find the parent container to determine which dimension this is
                            parent_container = ul.find_parent()
                            while parent_container and not any(cls in parent_container.get('class', []) for cls in ['dimention-chart1', 'dimention-chart2', 'dimention-chart3']):
                                parent_container = parent_container.find_parent()
                            
                            if parent_container:
                                classes = parent_container.get('class', [])
                                if 'dimention-chart1' in classes:
                                    individual_scores["environmental"] = score
                                    self.logger.log("debug", f"Found Environmental score: {score}")
                                elif 'dimention-chart2' in classes:
                                    individual_scores["social"] = score
                                    self.logger.log("debug", f"Found Social score: {score}")
                                elif 'dimention-chart3' in classes:
                                    individual_scores["governance"] = score
                                    self.logger.log("debug", f"Found Governance score: {score}")
                        except ValueError:
                            self.logger.log("warning", f"Could not parse score as integer: {score_text}")
                            continue

            # Method 2: Look for JSON data in script tags
            if not any(individual_scores.values()):
                self.logger.log("debug", "Trying to find scores in script tags")
                import re
                import json
                
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string:
                        script_content = script.string
                        
                        # Look for JSON objects that might contain scores
                        json_patterns = [
                            r'("environmental":\s*\d+)',
                            r'("social":\s*\d+)',
                            r'("governance":\s*\d+)',
                            r'(\{\s*[^}]*(?:environmental|social|governance)[^}]*\})',
                        ]
                        
                        for pattern in json_patterns:
                            matches = re.findall(pattern, script_content, re.IGNORECASE)
                            for match in matches:
                                try:
                                    if match.startswith('{'):
                                        # Full JSON object
                                        data = json.loads(match)
                                        if isinstance(data, dict):
                                            for key, value in data.items():
                                                if isinstance(value, (int, float)):
                                                    if 'environmental' in key.lower():
                                                        individual_scores["environmental"] = int(value)
                                                    elif 'social' in key.lower():
                                                        individual_scores["social"] = int(value)
                                                    elif 'governance' in key.lower():
                                                        individual_scores["governance"] = int(value)
                                    else:
                                        # Individual key-value pair
                                        if 'environmental' in match.lower():
                                            score_match = re.search(r'(\d+)', match)
                                            if score_match:
                                                individual_scores["environmental"] = int(score_match.group(1))
                                        elif 'social' in match.lower():
                                            score_match = re.search(r'(\d+)', match)
                                            if score_match:
                                                individual_scores["social"] = int(score_match.group(1))
                                        elif 'governance' in match.lower():
                                            score_match = re.search(r'(\d+)', match)
                                            if score_match:
                                                individual_scores["governance"] = int(score_match.group(1))
                                except (json.JSONDecodeError, ValueError):
                                    continue

            # Method 3: Text pattern matching in the full page content
            if not any(individual_scores.values()):
                self.logger.log("debug", "Trying regex pattern matching on page content")
                import re
                
                page_text = soup.get_text()
                
                # Look for patterns like "Environmental 45" or "Environmental: 45"
                env_pattern = r'environmental\s*:?\s*(\d+)'
                social_pattern = r'social\s*:?\s*(\d+)'
                gov_pattern = r'governance\s*:?\s*(\d+)'
                
                env_match = re.search(env_pattern, page_text, re.IGNORECASE)
                if env_match:
                    try:
                        individual_scores["environmental"] = int(env_match.group(1))
                        self.logger.log("debug", f"Found Environmental score via regex: {env_match.group(1)}")
                    except ValueError:
                        pass
                
                social_match = re.search(social_pattern, page_text, re.IGNORECASE)
                if social_match:
                    try:
                        individual_scores["social"] = int(social_match.group(1))
                        self.logger.log("debug", f"Found Social score via regex: {social_match.group(1)}")
                    except ValueError:
                        pass
                
                gov_match = re.search(gov_pattern, page_text, re.IGNORECASE)
                if gov_match:
                    try:
                        individual_scores["governance"] = int(gov_match.group(1))
                        self.logger.log("debug", f"Found Governance score via regex: {gov_match.group(1)}")
                    except ValueError:
                        pass

            # Method 4: Look for chart titles and data attributes
            if not any(individual_scores.values()):
                self.logger.log("debug", "Trying chart title approach to find individual scores")
                
                charts = soup.select('[id^="DimensionScore_"]')
                for chart in charts:
                    # Find the title
                    title_element = chart.select_one('.highcharts-title')
                    if title_element:
                        title = title_element.get_text(strip=True).lower()
                        
                        # Find the corresponding score list
                        parent = chart.find_parent()
                        if parent:
                            ul = parent.select_one('.DimensionScore__label ul li span')
                            if ul:
                                try:
                                    score = int(ul.get_text(strip=True))
                                    if 'environmental' in title:
                                        individual_scores["environmental"] = score
                                        self.logger.log("debug", f"Found Environmental score (chart method): {score}")
                                    elif 'social' in title:
                                        individual_scores["social"] = score
                                        self.logger.log("debug", f"Found Social score (chart method): {score}")
                                    elif 'governance' in title:
                                        individual_scores["governance"] = score
                                        self.logger.log("debug", f"Found Governance score (chart method): {score}")
                                except ValueError:
                                    continue

            # Method 5: Look for data attributes and various score selectors
            if not any(individual_scores.values()):
                self.logger.log("debug", "Trying various score selectors")
                
                score_selectors = [
                    "[data-dimension] .score-value",
                    "[data-dimension] .score",
                    ".dimension-score-value",
                    ".esg-dimension .score",
                    "[class*='dimension'] [class*='score']",
                ]
                
                for selector in score_selectors:
                    elements = soup.select(selector)
                    for elem in elements:
                        score_text = elem.get_text(strip=True)
                        if score_text.isdigit():
                            score = int(score_text)
                            
                            # Try to determine dimension from context
                            context_elem = elem.find_parent()
                            context_text = ""
                            for i in range(3):  # Check up to 3 parent levels
                                if context_elem:
                                    context_text += str(context_elem).lower()
                                    context_elem = context_elem.find_parent()
                                else:
                                    break
                            
                            if 'environmental' in context_text or 'environment' in context_text:
                                individual_scores["environmental"] = score
                                self.logger.log("debug", f"Found Environmental score via selector: {score}")
                            elif 'social' in context_text:
                                individual_scores["social"] = score
                                self.logger.log("debug", f"Found Social score via selector: {score}")
                            elif 'governance' in context_text:
                                individual_scores["governance"] = score
                                self.logger.log("debug", f"Found Governance score via selector: {score}")
            
            self.logger.log("debug", f"Individual scores for company {company_id}: {individual_scores}")
            return individual_scores
            
        except Exception as e:
            self.logger.log("error", f"Error extracting individual ESG scores for company {company_id}: {e}")
            return individual_scores

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

def init(company_names):
    """Test the S&P Global scraper with a list of company names and print results."""
    scraper = WebScraper(company_names)
    print("ESG Scores:", scraper.company_scores)
    
    
    print("ESG scores saved to:", OUTPUT_FILE)

if __name__ == "__main__":
    db = Database()
    companies = db.list_companies()
    print(f"Companies to process: {companies}")

    # Example usage: replace with your own list to test
    init(companies)


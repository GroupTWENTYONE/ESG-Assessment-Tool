# Web Scraping Documentation

## Overview

The ESG Assessment Tool uses various web scraping modules to collect ESG data from external sources. The main focus is on S&P Global ESG scores and sustainability reports from companies.

## S&P Global ESG Scraper

### Purpose and Functionality

The S&P Global Scraper (`spglobalScraper.py`) collects ESG scores and individual Environmental, Social, and Governance scores from the S&P Global website.

### Main Components

#### WebScraper Class

The `WebScraper` class is the core of the S&P Global scraper:

```python
class WebScraper:
    def __init__(self, company_names=None):
        self.logger = Logger("spglobal_scraper")
        self.company_scores = {}
        # Automatic scraping when company_names are provided
```

### API Endpoints

#### Search Endpoint

- **URL**: `https://www.spglobal.com/esg/csa/esg-proxy?comp-name={company_name}`
- **Purpose**: Find company ID for given company name
- **Returns**: JSON with company data and ID

#### Score Endpoint

- **URL**: `https://www.spglobal.com/esg/scores/results?cid={company_id}`
- **Purpose**: Retrieve ESG scores for given company ID
- **Returns**: HTML page with ESG score data

### Scraping Workflow

#### 1. Search Companies

```python
def search_company(self, company_name):
    """Searches for company ID via name"""
    # HTTP request with specific headers for S&P Global
    # Parse JSON response
    # Return first company ID
```

#### 2. Retrieve ESG Scores

```python
def get_esg_score(self, company_id):
    """Retrieves ESG scores via company ID"""
    # Load HTML page
    # BeautifulSoup for HTML parsing
    # Extract overall score and individual scores
```

#### 3. Extract Individual Scores

The scraper uses multiple methods for score extraction:

##### Method 1: Data-Score Attributes

```python
# Search for specific div elements with data-score attributes
env_div = soup.find("div", id="dimentions-score-env")
social_div = soup.find("div", id="dimentions-score-social")
gov_div = soup.find("div", id="dimentions-score-govecon")
```

##### Method 2: DimensionScore\_\_label Sections

```python
# Analysis of dimension score labels
dimension_labels = soup.select(".DimensionScore__label ul")
```

##### Method 3: JSON Data in Script Tags

```python
# Regex-based search in JavaScript code
json_patterns = [
    r'("environmental":\s*\d+)',
    r'("social":\s*\d+)',
    r'("governance":\s*\d+)'
]
```

##### Method 4: Text Pattern Matching

```python
# Regex search in entire page text
env_pattern = r'environmental\s*:?\s*(\d+)'
social_pattern = r'social\s*:?\s*(\d+)'
gov_pattern = r'governance\s*:?\s*(\d+)'
```

### HTTP Headers and Anti-Bot Measures

The scraper uses realistic browser headers:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:137.0) Gecko/20100101 Firefox/137.0",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "X-Requested-With": "XMLHttpRequest",    "Referer": "https://www.spglobal.com/esg/solutions/esg-scores-data",
    # Additional headers for authenticity
}
```

### Database Storage

Extracted scores are automatically stored in MongoDB:

```python
# Store overall ESG score
db.set_spglobal_esg_score(db_id, overall_score)

# Store individual scores
db.set_spglobal_individual_scores(
    db_id,
    environmental=individual_scores.get("environmental"),
    social=individual_scores.get("social"),
    governance=individual_scores.get("governance")
)
```

### Logging and Error Handling

#### Comprehensive Logging

- **Debug**: Detailed information about each step
- **Info**: Successful operations
- **Warning**: Missing data or companies not found
- **Error**: Network errors, HTTP errors, parsing errors

#### Error Handling

```python
try:
    # Scraping operation
except requests.exceptions.Timeout:
    self.logger.log("error", f"Timeout occurred...")
except requests.exceptions.HTTPError as e:
    self.logger.log("error", f"HTTP error: {e}")
except requests.exceptions.RequestException as e:
    self.logger.log("error", f"Network error: {e}")
except Exception as e:
    self.logger.log("error", f"Unexpected error: {e}")
```

### Usage

#### Scrape Individual Companies

```python
from spglobalScraper.spglobalScraper import WebScraper

# Manual usage
scraper = WebScraper()
company_id = scraper.search_company("Apple Inc.")
score_data = scraper.get_esg_score(company_id)
```

#### Bulk Scraping

```python
# Automatic scraping for list of companies
company_names = ["Apple Inc.", "Microsoft Corporation", "Google"]
scraper = WebScraper(company_names)  # Automatically starts scraping
```

#### Database Integration

```python
# Scrape all companies from database
from databaseAccess.database import Database
db = Database()
companies = db.list_companies()
scraper = WebScraper(companies)
```

## Sustainability Reports Scraper

### ResponsibilityReports.com Scraper

The general web scraper (`webScraper.py`) collects sustainability reports from responsibilityreports.com:

#### Functionalities

1. **Retrieve S&P 500 Companies**: From Wikipedia list
2. **Find Company PDFs**: Search on responsibilityreports.com
3. **Download Reports**: Save PDFs for further analysis

#### Workflow

```python
def scrape(self):
    data = self.get_data()          # S&P 500 from Wikipedia
    companies = self.parse_companies(data)  # Extract company names
    self.download_reports(companies)        # Download PDFs in parallel
```

## Data Export for Machine Learning

### ML-Ready Data Export

The system provides specialized export functions for Machine Learning:

#### 1. Combined ESG Data (`export_esg_ml_ready_data.py`)

```python
def export_companies_to_json():
    # Combines E, S, G texts for each company
    # Output format: {"id": "...", "text": "combined ESG text", "score": 45.0}
    # Saves to: ML/ml_ready_data/ml_ready_esg_data.json
```

#### 2. Separated ESG Components (`export_esg_separeted_ml_ready_data.py`)

```python
def export_companies_to_json():
    # Separate files for E, S, G components
    # E-components → ml_ready_e.json
    # S-components → ml_ready_s.json
    # G-components → ml_ready_g.json
```

### Export Data Format

#### Combined Data

```json
[
  {
    "id": "67e073dd8db8d8dabadc5117",
    "text": "Environmental statements... Social statements... Governance statements...",
    "score": 45.0
  }
]
```

#### Separated Components

```json
[
  {
    "company_id": "67e073dd8db8d8dabadc5117",
    "texts": ["Environmental statement 1", "Environmental statement 2"],
    "esg_score": 45.0
  }
]
```

## Execution and Deployment

### Running Scrapers

#### S&P Global Scraper

```bash
cd DataColector/src/spglobalScraper
python spglobalScraper.py
```

#### Sustainability Reports

```bash
cd DataColector/src
python main.py  # activate run_web_scaper()
```

#### Data Export

```bash
cd DataColector/src/export_ml_ready_data
python export_esg_ml_ready_data.py
python export_esg_separeted_ml_ready_data.py
```

### Docker Integration

The scrapers can be run in Docker containers:

```dockerfile
FROM python:3.9
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/
WORKDIR /app/src
CMD ["python", "main.py"]
```

## Best Practices and Guidelines

### Rate Limiting

- Implement delays between requests
- Use `time.sleep()` for intensive scraping
- Respect robots.txt of target websites

### Error Handling

- Implement retry mechanisms
- Log all errors for debugging
- Use timeouts for HTTP requests

### Data Quality

- Validate extracted data
- Implement consistency checks
- Monitor changes in website structures

### Maintenance

- Regularly check CSS selectors
- Update User-Agent strings
- Monitor website changes

### Legal Considerations

- Respect Terms of Service
- Implement respectful scraping practices
- Consider copyrights of collected data

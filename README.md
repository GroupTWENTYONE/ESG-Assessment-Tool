# ESG-Assessment-Tool

> [!NOTE]  
> This project is under development <br>
> University Project
>

## Overview
The **ESG Assessment Tool** is an automated solution for evaluating a company's compliance with ESG (Environmental, Social, and Governance) criteria as defined by the EU. This tool simplifies data collection, analysis, and storage, providing businesses and investors with actionable insights for ESG compliance and sustainability investments.

## Features
- **Web Scraper**: Automatically collects ESG-relevant text documents from predefined sources.
- **Text Classification**: Analyzes and categorizes text data into ESG components (Environmental, Social, Governance) using advanced models:
  - [FinBERT-ESG (9 Categories)](https://huggingface.co/yiyanghkust/finbert-esg-9-categories)
  - [FinBERT-ESG](https://huggingface.co/yiyanghkust/finbert-esg)
- **Database Integration**: Stores results in a MongoDB database running in a Docker container.
- **Automation**: Seamlessly processes data for S&P 500 companies without manual intervention.

## Installation

Follow these steps to set up the ESG Assessment Tool on your local machine:

### Prerequisites
- **Python 3.11+**:
  - **Windows**: [Download Python](https://www.python.org/downloads/)
  - **Linux/macOS**: Python is usually pre-installed. If not, use your system's package manager to install it.

---

### Steps to Install

1. **Clone the Repository**:  
   a. Open a terminal and run:  
   ```bash
   git clone https://github.com/GroupTWENTYONE/ESG-Assessment-Tool.git
   ```
   b. Alternatively, download the ZIP file from the repository and extract it.
2. Navigate to the Project Folder:
    ```bash
    cd ESG-Assessment-Tool
    ```
3. Create a Virtual Environment:
- Linux/macOS
    ```bash
    python -m venv ./src/.venv
    source ./src/.venv/bin/activate
    ```
- Windows
    ```bash
    python -m venv .\src\.venv
    .\src\.venv\Scripts\activate
    ```
4. Install Project Dependencies:
    ```bash
    pip install -r ./src/requirements.txt
    ```
6. Run the Application:
    ```bash
    python ./src/main.py
    ```

## Usage
1. **Web Scraping**: Automatically downloads ESG-related documents.
2. **Text Classification**: Processes downloaded documents and categorizes them into ESG components.
3. **Data Storage**: Saves the processed results in a structured MongoDB database.

## Technologies Used
- **Programming Language**: Python
- **Database**: MongoDB (Docker-based deployment)
- **Machine Learning Models**: FinBERT-ESG from Hugging Face

## Current Status
- **Implemented Features**:
  - Web scraping for ESG-related data
  - Initial classification using FinBERT models
  - MongoDB database integration
- **In Progress**:
  - Optimization of web scraper performance
  - Scaling for additional data sources
  - Development of ESG-Score calculation

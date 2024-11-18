# Import libraries
import yfinance as yf
import pandas as pd
import os

# Set working directory
os.chdir("C:\\Users\\lauri\\Desktop\\INNOLAB")

# Load ticker data
djia = pd.read_csv("tickers.csv")
# Initialize an empty list to store ESG data
esg_data_list = []

# Loop through tickers
for i in djia['ticker_code']:
    i_y = yf.Ticker(i)
    try:
        # Check if sustainability data exists
        if i_y.sustainability is not None:
            temp = pd.DataFrame.transpose(i_y.sustainability)
            temp['company_ticker'] = str(i_y.ticker)
            esg_data_list.append(temp)
    except Exception as e:
        print(f"Fehler bei {i}: {e}")

# Combine all ESG data into a single DataFrame
esg_data = pd.concat(esg_data_list, ignore_index=True)

# Save ESG data to a CSV file
output_file = "esg_data.csv"
esg_data.to_json("esg_data.json", orient="records", lines=True)
print(f"ESG-Daten gespeichert unter: {os.path.abspath('esg_data.json')}")
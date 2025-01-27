import logging
import os
from transformers import pipeline, BertForSequenceClassification, BertTokenizer
from databaseAccess.database import Database

# Set up logging
class Logger:
    def __init__(self, company_name):
        self.logger = logging.getLogger(company_name)
        self.logger.setLevel(logging.DEBUG)

        log_folder = f"./logs"
        os.makedirs(log_folder, exist_ok=True)

        # Create file handler for the logger
        log_filename = f"{log_folder}/{company_name}.log"
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(logging.DEBUG)

        # Create a formatter and set it for the handler
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(file_handler)

    def log(self, level, message):
        if level == "info":
            self.logger.info(message)
        elif level == "warning":
            self.logger.warning(message)
        elif level == "error":
            self.logger.error(message)
        elif level == "debug":
            self.logger.debug(message)
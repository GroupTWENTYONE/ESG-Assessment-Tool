import json
import os
import torch.nn.functional as F
from transformers import pipeline, BertForSequenceClassification, BertTokenizer
import requests
import yfinance as yf

from databaseAccess.database import Database
from logger.logger import Logger


class ESGAnalyzer:
    def __init__(self):
             
        finbert4_model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-esg", num_labels=4)
        tokenizer_finbert4 = BertTokenizer.from_pretrained("yiyanghkust/finbert-esg")
        self.nlp_finbert4 = pipeline("text-classification", model=finbert4_model, tokenizer=tokenizer_finbert4)

        finbert9_model = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-esg-9-categories',num_labels=9)
        tokenizer_finbert9 = BertTokenizer.from_pretrained('yiyanghkust/finbert-esg-9-categories')
        self.nlp_finbert9 = pipeline("text-classification", model=finbert9_model, tokenizer=tokenizer_finbert9)

        self.base_path = "./prepared_data/"
        self.db = Database()
        self.logger = None

        self.thresholds = {
            "primary": 0.8,  # Primary classification threshold
            "override_margin": 0.1,  # Margin for subcategory override
            "weights": {"component": 0.7, "subcategory": 0.3, "mismatch_penalty": 0.5},
            "Environmental": {"subcategories": ["Climate Change", "Natural Capital", "Pollution & Waste"]},
            "Social": {"subcategories": ["Human Capital", "Product Liability", "Community Relations"]},
            "Governance": {"subcategories": ["Corporate Governance", "Business Ethics & Values"]}
        }

    def setup_logger(self, company_name):
        self.logger = Logger(company_name)

    def process_company(self, company_code: str):
        self.company_name = self.get_company_name(company_code)
        self.company_code = company_code

        self.setup_logger(self.company_name)
        self.logger.log("info", f"Processing company: {self.company_name} ({company_code})")

        # load documents
        try:
            for file in os.listdir(self.base_path + company_code):
                filename = os.fsdecode(file)
                file_content = self.load_json_file(self.build_file_path(company_code, filename))
                self.analyze(file_content)
        except Exception as e:
            self.logger.log("error", f"Error processing company {self.company_name}: {str(e)}")


    def build_file_path(self, company_code: str, filename: str):
        return self.base_path+company_code+"/"+filename

    @staticmethod
    def load_json_file(filename: str):
        """Loads a JSON file and returns its content."""
        with open(filename, 'r') as file:
            return json.load(file)

    @staticmethod
    def split_text_into_blocks(text, block_length=1024):
        """Splits a text into blocks of specified length."""
        return [text[i:i + block_length] for i in range(0, len(text), block_length)]

    def analyze(self, sentences):
        """Analyzes a list of sentences."""
        for i, sentence in enumerate(sentences):
            print(f"\nProcessing sentence {i + 1}:")
            self.logger.log("debug", f"Analyzing sentence {i + 1}")
            if len(sentence) > 1024:
                print("Block size too large, splitting into smaller blocks.")
                self.logger.log("warning", "Block size too large, splitting into smaller blocks.")
                sentence_blocks = self.split_text_into_blocks(sentence)
                for j, block in enumerate(sentence_blocks):
                    print(f"\nAnalyzing Sentence {i + 1}.{j + 1}:")
                    self.logger.log("debug", f"Analyzing sentence {i + 1}.{j + 1}")
                    self._analyze_block(block)
            else:
                self._analyze_block(sentence)

    def _analyze_block(self, block):
        """Analyzes a single block of text."""
        try:
            self.logger.log("debug", f"Current Block:\n{block}")

            result4 = self.nlp_finbert4(block)
            result9 = self.nlp_finbert9(block)

            self.process_result(result4, result9, block)
            
        except Exception as e:
            self.logger.log("error", f"Error analyzing block: {str(e)}")

    def process_result(self, result4, result9, block):
        print(result4)
        print(result9)
        
        json_data = json.dumps(result4)
        data4 = json.loads(json_data)

        json_data = json.dumps(result9)
        data9 = json.loads(json_data)

        esg_component = self.classify_esg(data4[0]['label'], data4[0]['score'], data9[0]['label'], data9[0]['score'])
        print(esg_component)
        
        if esg_component != "None":
            self.save_result(esg_component, block)
        else:
            self.logger.log("warning", f"Not relevant. Block skipped.")

    def save_result(self, label: str, block):
        # check if company exists in db
        company_id = self.db.get_company_id_by_ticker(self.company_code)
        if company_id == None:
            company_id = self.db.add_company(self.company_name, self.company_code)
        # add esg component
        self.db.add_esg_component(company_id, label[0].upper(), block)
        self.logger.log("info", f"Adding ESG component for {label}")

    def classify_esg(self, component: str, component_score, subcategory: str, subcategory_score) -> str:
        # Retrieve the subcategories for the given component
        if component != "None":
            valid_subcategories = self.thresholds[component]["subcategories"]
        else:
            valid_subcategories = []
        primary_threshold = self.thresholds["primary"]
        override_margin = self.thresholds["override_margin"]

        # Check if the subcategory aligns with the component
        if subcategory in valid_subcategories:
            # Weighted score calculation
            final_score = (
                self.thresholds["weights"]["component"] * component_score +
                self.thresholds["weights"]["subcategory"] * subcategory_score
            )
            # Classify based on thresholds
            if final_score >= primary_threshold:
                return component
            elif subcategory_score - component_score >= override_margin:
                return component  # Override if subcategory score is significantly higher
        elif component == "None":
            if subcategory_score > 0.85 and component_score < 0.6:
                return self.get_component_by_subcategory(subcategory)
            elif subcategory_score > 0.95:
                return self.get_component_by_subcategory(subcategory)
            else:
                return component
        else:
            # Penalize mismatched subcategories
            final_score = (
                self.thresholds["weights"]["component"] * component_score -
                self.thresholds["weights"]["mismatch_penalty"] * subcategory_score
            )
            if final_score >= primary_threshold:
                return component

        # Default to "None" if no strong match
        return "None"
    
    def get_component_by_subcategory(self, subcategory):
        for component, data in self.thresholds.items():
            if component in ["Environmental", "Social", "Governance"]:
                if subcategory in data["subcategories"]:
                    return component
        return "None"
    
    def get_company_name(self, symbol) -> str:
        msft = yf.Ticker(symbol)

        return msft.info['longName']

def main():

    analyzer = ESGAnalyzer()
    
    analyzer.process_company("Adobe", "ADBE")
    
    # for each company
    #   analyzer process_company


if __name__ == "__main__":
    main()

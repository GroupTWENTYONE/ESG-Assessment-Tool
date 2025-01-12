import json
import math
import argparse
import os
import torch.nn.functional as F
from transformers import pipeline, BertForSequenceClassification, BertTokenizer

class ESGAnalyzer:
    def __init__(self):
        # Load pre-trained ESG classification model
        # ADBE1.
             
        self.classifier_pipeline = pipeline("text-classification", model="yiyanghkust/finbert-esg")
        self.finbert_model = BertForSequenceClassification.from_pretrained("yiyanghkust/finbert-esg", num_labels=4)
        self.tokenizer = BertTokenizer.from_pretrained("yiyanghkust/finbert-esg")
        self.nlp = pipeline("text-classification", model=self.finbert_model, tokenizer=self.tokenizer)
        self.base_path = "./text-analysis/res/"

    
    def process_company(self, company_name, company_code):
        self.company_name = company_name
        self.company_code = company_code

        print(os.getcwd())
        # load documents
        for file in os.listdir(self.base_path + company_code):
            filename = os.fsdecode(file)
            file_content = self.load_json_file(self.build_file_path(company_code, filename))
            self.analyze(file_content)

    def build_file_path(self, company_code, filename):
        return self.base_path+company_code+"/"+filename

    @staticmethod
    def load_json_file(filename):
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

            if len(sentence) > 1024:
                print("Block size too large, splitting into smaller blocks.")
                sentence_blocks = self.split_text_into_blocks(sentence)
                for j, block in enumerate(sentence_blocks):
                    print(f"\nAnalyzing Sentence {i + 1}.{j + 1}:")
                    self._analyze_block(block)
            else:
                self._analyze_block(sentence)

    def _analyze_block(self, block):
        """Analyzes a single block of text."""
        result = self.nlp(block)
        print(result)

        inputs = self.tokenizer(block, return_tensors="pt", truncation=True)
        raw_result = self.finbert_model(**inputs)
        logits = raw_result.logits
        probabilities = F.softmax(logits, dim=1)

        labels = ['None', 'Environmental', 'Social', 'Governance']
        results = dict(zip(labels, [round(float(x), 4) for x in probabilities.detach().numpy()[0]]))
        print(results)


def main():

    analyzer = ESGAnalyzer()
    
    analyzer.process_company("Adobe", "ADBE")
    
    # for each company
    #   analyzer process_company


if __name__ == "__main__":
    main()

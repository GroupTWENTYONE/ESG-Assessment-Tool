import PyPDF2
import os
import json
import re

DATA_DIR = "./raw_data/"
PREPARED_DATA_DIR = "./prepared_data/"
PDF_EXT = ".pdf"
JSON_EXT = "_formatted.json"
BLOCK_LENGTH = 1024

class DocumentProcessor:
    @staticmethod
    def extract_text_from_pdf(filename):
        """Extracts text from a PDF file."""
        try:
            with open(f"{DATA_DIR}{filename}", 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                return ''.join(page.extract_text() for page in pdf.pages)
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            return None

    @staticmethod
    def create_blocks(text, block_length=BLOCK_LENGTH):
        """Splits text into blocks of a specified length, respecting sentence boundaries."""
        i = 0
        blocks = []
        while i < len(text):
            line = text[i:i+block_length]
            for ii in range(len(line)):
                if line[-1 - ii] in ['.', ' ']:
                    blocks.append(line[:len(line)-1 - ii])
                    i = i - ii
                    break
            i += block_length
        return blocks

    @staticmethod
    def clean_text(json_text):
        """Cleans text by replacing special characters and reducing whitespace."""
        replacements = {
            '\u00A0': ' ', '\u202F': ' ', '\u00a9': "'", '\u02bb': "'",
            '\u02bc': "'", '\u2019': "'", '\u2014': '-', '\u2013': '-',
            '\u25a0': '-', '\u2022': '-', '\u201d': '"', '\u201c': '"',
            '\u00b0': '°', '\u00ba': '°'
        }

        cleaned_text = []
        for text in json_text:
            for old, new in replacements.items():
                text = text.replace(old, new)

            text = re.sub(r'[\n\t\r]', ' ', text)
            text = re.sub(r'\s+', ' ', text).strip()
            cleaned_text.append(text)

        return cleaned_text

    @staticmethod
    def process_pdf(filename: str, split_into_lines):
        """Processes a PDF file and saves the formatted data as JSON."""
        if split_into_lines:
            text = DocumentProcessor.extract_text_from_pdf(filename)
            array_data = DocumentProcessor.create_blocks(text)
        else:
            array_data = DocumentProcessor.extract_text_from_pdf(filename).splitlines()

        array_data = DocumentProcessor.clean_text(array_data)
        error = False
        start_index = filename.index('_') + 1
        end_index = filename.index('_', start_index)
        company_code = filename[start_index:end_index]
        os.makedirs(f"{PREPARED_DATA_DIR}/{company_code}", exist_ok=True)
        try:
            with open(f"{PREPARED_DATA_DIR}{company_code}/{filename.replace(PDF_EXT, JSON_EXT)}", 'w') as outfile:
                json.dump(array_data, outfile, indent=2)
        except IOError as e:
            print(f"Error saving result of {filename}: {e}")
            error = True

        return not error

    @staticmethod
    def process_all_pdfs(split_into_lines):
        """Processes all PDF files in the data directory."""
        for filename in os.listdir(DATA_DIR):
            if not filename.endswith(PDF_EXT):
                continue

            if DocumentProcessor.process_pdf(filename, split_into_lines):
                print(f"{filename} processed")
            else:
                print(f"{filename} failed")

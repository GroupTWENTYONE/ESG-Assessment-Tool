import json
import PyPDF2
import os

def extract_text_from(filename):

    try:
        with open(f"../data/{filename}", 'rb') as file:
            pdf = PyPDF2.PdfReader(file)
            text = ''.join(page.extract_text() for page in pdf.pages)
            return text
    except Exception as e:
        print(f"Error processing {filename}: {e}")
        return None
    
def to_string_array(text):

    data = text.split(". ")
    '''
    for line in data:
        print("\nTHIS IS A SINGLE LINE: --------------------------------")
        print(line)
        print("\n")
    '''
    return data
    
def process_pdf(filename) -> bool:
    # extract text 
    extracted_text = extract_text_from(filename)
    
    # transform into output format
    array_data = to_string_array(extracted_text)

    error = False

    #json_data = {line for line in array_data}
    # save 
    try:
        with open(f"../formatted_data/{filename.replace('.pdf', '_formatted.json')}", 'w') as outfile:
            json.dump(array_data, outfile, indent=2)
    except IOError as e:
        print(f"Error saving result of {filename}: {e}")
        error = True
    
    #remove pdf
    '''
    try:
        os.remove(f"../data/{filename}")
    except OSError as e:
        print(f"Error removing pdf of {filename}: {e}")
        error = True
    '''
    
    return False if error else True

def process_data():
    #filenames = ["NASDAQ_AAPL_2022.pdf"]

    for filename in os.listdir("../data/"):
        if not filename.endswith(".pdf"):
            continue
        if process_pdf(filename) :
            print(f"{filename} processed")
        else :
            print(f"{filename} failed")



def clear_cache():
    for filename in os.listdir("../formatted_data/"):
        try:
            os.remove(f"../formatted_data/{filename}")
        except OSError as e:
            print(f"Error removing pdf of {filename}: {e}")
            return False
    

#clear_cache()

if __name__ == "__main__":
    process_data()
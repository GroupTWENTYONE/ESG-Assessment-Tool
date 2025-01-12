import json
from transformers import pipeline, BertForSequenceClassification, BertTokenizer
import numpy as np
import math
import torch.nn.functional as F


def create_blocks(text, block_length = 1024):
    i=0
    f=[]
    while(i<len(text)):
        f.append(text[i:i+block_length])
        i+=block_length
    return f

def getJsonFromFile(filename):
    with open(filename, 'r') as file:
        data = json.load(file)
    return data

def analyse(json_data): 

    for i, sentence in enumerate(json_data):
        print(f"\nProcessing sentence {i + 1}:\n")


        if(len(sentence) > 1024):
            print("block size to big")
            block_count = math.ceil(len(sentence)/1024)
            print(block_count)
            sentence_blocks = create_blocks(sentence)

            for j, block in enumerate(sentence_blocks):
                print(f"\nSentence {i + 1}.{j+1}")
                analyse_block(block)
            continue

        analyse_block(sentence)

    return

def analyse_block(block):
    #print(block)
    result = nlp(block)
    print(result)
    input = tokenizer(block, return_tensors="pt", truncation = True)
    resultraw = finbert(**input)
    logits = resultraw.logits
    probabilities = F.softmax(logits, dim=1)
    labels = ['None', 'Environmental', 'Social', 'Governance']
    results = dict(zip(labels, [round(float(x),4) for x in probabilities.detach().numpy()[0]]))
    print(results)
    #handle result

if __name__ == "__main__":
    # Load pre-trained ESG classification model
    classifier = pipeline("text-classification", model="yiyanghkust/finbert-esg")
    finbert = BertForSequenceClassification.from_pretrained('yiyanghkust/finbert-esg',num_labels=4)
    tokenizer = BertTokenizer.from_pretrained('yiyanghkust/finbert-esg')
    nlp = pipeline("text-classification", model=finbert, tokenizer=tokenizer)

    json_data = getJsonFromFile("text-analysis/res/NASDAQ_ADBE_2023_formatted.json")
    analyse(json_data)



from bs4 import BeautifulSoup
import json
import numpy as np
import requests
from requests.models import MissingSchema
import spacy
import trafilatura
import lxml
from constant import apiKey

def beautifulsoup_extract_text_fallback(response_content):
    
    '''
    This is a fallback function, so that we can always return a value for text content.
    Even for when both Trafilatura and BeautifulSoup are unable to extract the text from a 
    single URL.
    '''
    
    # Create the beautifulsoup object:
    soup = BeautifulSoup(response_content, 'html.parser')
    
    # Finding the text:
    text = soup.find_all(string=True)
    
    # Remove unwanted tag elements:
    cleaned_text = ''
    blacklist = [
        '[document]',
        'noscript',
        'header',
        'meta',
        'html',
        'head', 
        'input',
        'script',
        'style',
        'nav',
        'footer']

    # Then we will loop over every item in the extract text and make sure that the beautifulsoup4 tag
    # is NOT in the blacklist
    for item in text:
        if item.parent.name not in blacklist:
            cleaned_text += '{} '.format(item)
            
    # Remove any tab separation and strip the text:
    cleaned_text = cleaned_text.replace('\t', '')
    
    
    return cleaned_text.strip()




headers = {'Accept': 'application/json'}

articleSources = requests.get('https://newsapi.org/v2/everything?q=samsungs&from=2024-11-15&sortBy=publishedAt&apiKey='+apiKey)
#print(f"Response: {x.json()}")
jsonString = articleSources.json()




articles_array = []

for article in jsonString["articles"]:
    parsed_article = [
        article["source"]["id"],
        article["source"]["name"],
        article["author"],
        article["title"],
        article["description"],
        article["url"],
        article["urlToImage"],
        article["publishedAt"],
        article["content"]
    ]
    articles_array.append(parsed_article)



# Print the 2D array
#for index, article in enumerate(articles_array, 1):
    #print(f"Article {index}: {article}")
    
    

# Extract only the URLs from articles_array
urls = [article[5] for article in articles_array]  # Index 5 corresponds to the URL in the sublist

# Print the URLs
#for url in urls:
#    print(url)

data = {}
f = open("../data/demofile2.txt", "a",encoding="utf-8")
for url in urls:
    # 1. Obtain the response:
    resp = requests.get(url)
    
    # 2. If the response content is 200 - Status Ok, Save The HTML Content:
    if resp.status_code == 200:
        data[url] = resp.text  
        #print(url)
        #print(beautifulsoup_extract_text_fallback(resp.content))
        text = beautifulsoup_extract_text_fallback(resp.content)
        #print(text)
        
        f.write(text)
        
    else:
        print("Error Site not reached")
 
f.close()


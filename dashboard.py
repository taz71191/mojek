import spacy
import re
import requests
import pandas as pd
import streamlit as st

nlp = spacy.load("./mojek_pipeline")

google_api_key = 'AIzaSyAEclAraZx1QXVEY_rpV_2v_Vca9A_-rYI'

search_engine_id = '7351b00a1bb194df8'


def extract_google_query(nlp, narration):
    query = narration
    remov_pcd = r'[^PCD/]' #Personal Certificate of Deposit
    pattern = r'[0-9:/]'
    # mod_string = re.sub(remov_pcd, ' ', query)
    # Match all digits in the string and replace them by empty string
    mod_string = query.replace('PCD', '')
    mod_string = query.replace('POS', '')
    mod_string = query.replace('XXXXXX', '')
    mod_string = re.sub(pattern, ' ', mod_string)
    # using the first page
    page = 1
    # constructing the URL
    # doc: https://developers.google.com/custom-search/v1/using_rest
    # calculating start, (page=2) => (start=11), (page=3) => (start=21)
    start = (page - 1) * 10 + 1
    url = f"https://www.googleapis.com/customsearch/v1?key={google_api_key}&cx={search_engine_id}&q={mod_string}&start={start}"
    data = requests.get(url).json()
    if 'items' in data.keys():
        for item in data['items']:
            if 'snippet' not in item.keys():
                continue
            snippet = item['snippet']
            doc1 = nlp(snippet.lower())
            if len(doc1.ents) >= 1:
                if doc1.ents[0].label_ not in labels:
                    continue
                else:
                    st.write(doc1)
                    return doc1.ents[0].label_
    else:
        'No match'

def expense_tracker(nlp, narration, labels, version='v2'):
    doc1 = nlp(narration.lower())
    if len(doc1.ents) >= 1:
        for doc in doc1.ents:
            label = doc.label_
            if label in labels:
                return label
            else:
                continue
    if version == 'v2':
        st.write("Using Google Search")
        label = extract_google_query(nlp, narration)
        return label
    else:
        return 'No match'


labels = ['Credit Card Payment', 'Equity', 'Crypto', 'Savings', 'Phone',
       'Household Expenses', 'Pet', 'General Expenses', 'Fuel', 'Retail',
       'Online Shopping', 'Streaming', 'Flight', 'Hotel', 'Local travel',
       'Restaurants', 'Work Expenses', 'Online News', 'Uber',
       'ATM Withdrawal']

st.title("Mojek Expense Tracker Demo")

user_input = st.text_input("Enter your expense here")


st.text(expense_tracker(nlp, user_input, labels))

import spacy
import re
import requests
import pandas as pd
import streamlit as st
from shillelagh.backends.apsw.db import connect

nlp = spacy.load("./mojek_pipeline")

google_api_key = st.secrets["google_api_key"]
gcp_service_account = st.secrets['gcp_service_account']


search_engine_id = st.secrets["search_engine_id"]
private_g_sheet_url = st.secrets["private_g_sheet_url"]
conn = connect(":memory:", adapter_kwargs={"gsheetsapi": {"service_account_info": gcp_service_account}})

NoneType = type(None)

def save_to_google(user_name, user_age, user_occupation, narration, keyword, user_label):
    cursor = conn.cursor()
    query = f"""INSERT INTO '{private_g_sheet_url}' (user_name, user_age, user_occupation, narration, keyword, label)
    VALUES ('{user_name}', '{user_age}', '{user_occupation}', '{narration}', '{keyword}','{user_label}')
    """
    # st.write(query)
    cursor.execute(query)
    conn.commit()
    st.session_state.narration = ""

def extract_google_query(nlp, narration, google_api_key=google_api_key, search_engine_id=search_engine_id):
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
            if (len(doc1.ents) >= 1) & (type(doc1.ents) != NoneType):
                if doc1.ents[0].label_ not in labels:
                    continue
                else:
                    st.write(doc1)
                    return doc1.ents[0].label_
            else:
                continue
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
labels.sort()

if 'user_label' not in st.session_state:
    st.session_state.user_label = None
if 'user_name' not in st.session_state:
    st.session_state.user_name = None
if 'user_age' not in st.session_state:
    st.session_state.user_age = None
if 'user_occupation' not in st.session_state:
    st.session_state.user_occupation = None
if 'narration' not in st.session_state:
    st.session_state.narration = None
if 'keyword' not in st.session_state:
    st.session_state.keyword = None

# if st.session_state.user_label != None:
#     save_to_google(st.session_state.user_name, st.session_state.user_age, st.session_state.user_occupation, st.session_state.narration, st.session_state.keyword, st.session_state.user_label)
#     st.session_state.user_label = ''

st.title("Mojek Expense Tracker Demo")

colx, coly, colz = st.columns([1, 0.5, 0.5])
with colx:
    user_name = st.text_input("Enter your name")
with coly:
    user_age = st.text_input("Enter your age")
with colz:
    user_occupation = st.text_input("Enter your occupation")

narration = st.text_input("Enter your expense here")

if narration != "":
    st.text(expense_tracker(nlp, narration, labels))
    # st.write("Please let us know how we did")
    # col1, col2 = st.columns([0.5,0.5])
    # with col1:
    #     right = st.button('Right')
    # with col2:
    #     wrong = st.button('Wrong')
    
    
    # Ask for further details
    st.write("Please tell us what you would pick")
    # form = st.form(key='my_form')
    st.session_state.user_label = st.selectbox("Pick a label", labels)
    keyword = st.text_input("What would you say is the keyword in the narration",value=narration)
    # save = form.form_submit_button('Save', on_click=save_to_google, kwargs={"user_name":user_name, "user_age":user_age, "user_occupation":user_occupation, "narration":narration, "keyword":keyword, "user_label":st.session_state.user_label})    
    # save = form.form_submit_button('Save')
    # if save:
    #     save_to_google(user_name, user_age, user_occupation, narration, keyword, st.session_state.user_label)
    save = st.button('Save')

    if save:
        save_to_google(user_name, user_age, user_occupation, narration, keyword, st.session_state.user_label)


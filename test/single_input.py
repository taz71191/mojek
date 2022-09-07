from mojek_service.expense_tracker import expense_tracker, update_gsheet, income_tracker
from mojek_service.config import *
from mojek_service.labels import labels_expenses, labels_income
from mojek_service.config import *
import os
import spacy
import pandas as pd
import pdb
# https://dev.to/techparida/how-to-deploy-a-flask-app-on-heroku-heb
# https://stackoverflow.com/questions/57922676/exposing-an-endpoint-for-a-python-program

nlp = income_tracker(spacy.load("./mojek_pipeline"))

# narration = input("ENTER INPUT")
narration = 'upi/9812/'
narration_dict_w_category = {
    "narration": narration,
    "institution_name": "Kotak",
    "transaction_type": "Income"
}
response = expense_tracker(nlp, labels_income, google_api_key, search_engine_id, narration_dict_w_category)

label = response["label"]
print(response)



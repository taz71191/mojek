from mojek_service.expense_tracker import expense_tracker, update_gsheet
from mojek_service.config import *
from mojek_service.labels import labels
from mojek_service.config import *
import os
import spacy
import pandas as pd
import pdb
# https://dev.to/techparida/how-to-deploy-a-flask-app-on-heroku-heb
# https://stackoverflow.com/questions/57922676/exposing-an-endpoint-for-a-python-program

nlp = spacy.load("./mojek_pipeline")


narration = input("ENTER")
response = expense_tracker(nlp, narration, labels, google_api_key, search_engine_id)

label = response["label"]



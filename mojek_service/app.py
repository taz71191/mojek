from mojek_service.expense_tracker import expense_tracker
from mojek_service.config import *
from flask import Flask
from flask import request
from mojek_service.labels import labels
from mojek_service.config import *
from multiprocessing import Process
import os
import spacy

# https://dev.to/techparida/how-to-deploy-a-flask-app-on-heroku-heb
# https://stackoverflow.com/questions/57922676/exposing-an-endpoint-for-a-python-program

nlp = spacy.load("./mojek_pipeline")

app = Flask(__name__)

@app.route("/expense-tracker", methods=['GET'])
def get_expense_category():
    if request.method == 'GET':
        narration = request.args.get('input', None)
        print("Printing secrets:", google_api_key, search_engine_id)
        label = expense_tracker(nlp, narration, labels, google_api_key, search_engine_id)
        response = {"label": label}
        return response
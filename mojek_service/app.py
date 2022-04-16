from mojek_service.expense_tracker import expense_tracker, update_gsheet
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

@app.route("/")
def hello():
    return "Hello, send me your expense using https://enigmatic-plateau-09140.herokuapp.com/expense-tracker?narration={narration}"

@app.route("/expense-tracker", methods=['GET', 'POST'])
def get_expense_category():
    if request.method == 'GET':
        narration = request.args.get('narration', None)
        response = expense_tracker(nlp, narration, labels, google_api_key, search_engine_id)
        response["narration"] = narration
        return response
    elif request.method == 'POST':
        request_data = request.get_json()
        print("This is the request", request_data)
        response = update_gsheet(request_data)
        return response

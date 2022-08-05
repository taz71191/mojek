from mojek_service.expense_tracker import expense_tracker, update_gsheet
from mojek_service.config import *
from flask import Flask
from flask import request
from flask_cors import CORS
from mojek_service.labels import labels
from mojek_service.config import *
from multiprocessing import Process
import os
import spacy

# https://dev.to/techparida/how-to-deploy-a-flask-app-on-heroku-heb
# https://stackoverflow.com/questions/57922676/exposing-an-endpoint-for-a-python-program

nlp = spacy.load("./mojek_pipeline")

app = Flask(__name__)
cors = CORS(app)

@app.route("/")
def hello():
    return """Hello, send me your expense using https://enigmatic-plateau-09140.herokuapp.com/expense-tracker?narration={narration}
    OR Upload statement to https://enigmatic-plateau-09140.herokuapp.com/upload-statement?user-id=<>&institution_name=<>&file_type=<>&bankstatement=<>
    """

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

@app.route("/upload-statement", methods=['GET', 'POST'])
def parse_bank_statement():
    if request.method == 'GET':
        user_id = request.args.get('user_id', None)
        institution_name = request.args.get('institution_name', None)
        file_type = request.args.get('file_type', None)
        blob = request.args.get('body', None)
        print(blob)
        response = {"status": 200}
        return response
    elif request.method == 'POST':
        user_id = request.args.get('user_id', None)
        institution_name = request.args.get('institution_name', None)
        file_type = request.args.get('file_type', None)
        bank_statement = request.args.get('bank_statement', None)
        # data = request.get_json()
        # print(data)
        response = {"status": 200}
        return response

from mojek.expense_tracker import expense_tracker
from mojek.config import *
from flask import Flask
from flask import request
from mojek.labels import labels
from mojek.config import *
from multiprocessing import Process

import spacy

nlp = spacy.load("./mojek_pipeline")

app = Flask(__name__)

@app.route("/categories-expense")
def get_expense_category():
    narration = request.args.get('narration')
    label = expense_tracker(nlp, narration, labels, google_api_key, search_engine_id)
    response = {"label": label}
    return response
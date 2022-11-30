import re
from pymongo import MongoClient
from bson.objectid import ObjectId
from mojek_service.config import MONGODB_URL

def connect(connect_str):
    try:
        conn = MongoClient(connect_str)
        print("Connected successfully!!!")
        return conn
    except:  
        print("Could not connect to MongoDB")

def get_user_overrides(user_id):
    conn = connect(MONGODB_URL)
    db = conn['myFirstDatabase']
    user_id = str(user_id)
    user_id_Object = ObjectId(user_id)
    query = { "user": user_id_Object, "prev_category_name": {"$exists":True}}
    doc = db['transactions'].find(query)
    user_overrides = []
    for row in doc:
        user_overrides.append(row)
    return user_overrides

def clean_narration(narration):
    order = r'\d+'
    cleaned_narration = re.sub(order, '', narration)
    return cleaned_narration

def apply_overrides(user_id, doc_w_category):
    user_overrides = get_user_overrides(user_id)
    doc_w_category['cleaned_narration'] = doc_w_category['narration'].apply(clean_narration)
    for row in user_overrides:
        narration = row["narration"]
        cleaned_narration = clean_narration(narration)
        apply_all = row["apply_all"]
        category_name = row["category_name"]
        if apply_all == True:
            filtered_rows = doc_w_category.cleaned_narration == cleaned_narration
            doc_w_category.loc[filtered_rows, 'category_name'] = category_name
        else:
            filtered_rows = doc_w_category.cleaned_narration == narration
            doc_w_category.loc[filtered_rows, 'category_name'] = category_name
    return doc_w_category

        



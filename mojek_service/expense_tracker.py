import pandas as pd
import glob
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span
import re
import requests
from mojek_service.labels import labels
from mojek_service.config import *
NoneType = type(None)


# nlp = spacy.load("en_core_web_sm")
# matcher = Matcher(nlp.vocab)

def add_event_ent(matcher, doc, i, matches):
    # Get the current match and create tuple of entity label, start and end.
    # Append entity to the doc's entity. (Don't overwrite doc.ents!)
    match_id, start, end = matches[i]
    entity = Span(doc, start, end)
    # print(entity.text, entity.label_)
    try:
        label = nlp.vocab.strings[matches[0][0]]
    except:
        "Vocab issue"

def return_label(matcher, narration, debug=False):
    """
    Returns categorization label from narration
    debug flag idenitfies keywords which matched rule
    """
    doc = nlp(narration.lower())
    matches = matcher(doc)
    if debug:
        print([token.text for token in doc])
        print(matches)
    if len(matches) > 0:
        try:
            label = nlp.vocab.strings[matches[0][0]]
        except:
            label = "Vocab issue"
        return label
    else:
        return "General Expenses: Else"

def get_mapping_file(location = '/Users/murtazavahanvaty/Desktop/Mojek/pattern_matching_rules.xlsx'):
    mapping_file = pd.read_excel(location)
    return mapping_file


def add_keyword_to_mapping_file(category, 
    subcategory, 
    keyword, 
    user_type=0, 
    user_id=0,
    db=1,
    cr=0,
    save=True,
    mapping_file=None,
    location = '/Users/murtazavahanvaty/Desktop/Mojek/pattern_matching_rules.xlsx'):
    """
    Returns mapping file after adding the keyword
    If no mapping file is specified it will pull from location
    Fields required to add keyword:
        category, 
        subcategory, 
        keyword, 
        user_type=0, 
        user_id=0,
        db=1,
        cr=0,
    """

    # Mapping dictionary
    if mapping_file == None:
        mapping_file = pd.read_excel(location)
    # Adding keywords to mapping file
    
    keyword_dict = {'Category': f'{category}',
        'Subcategory': f'{subcategory}',
        'Keyword': f'{keyword}',
        'User_type': user_type,
        'User_id': user_id,
        'DB': db,
        'CR': cr}

    mapping_file = pd.concat([mapping_file, pd.DataFrame(keyword_dict, index=[0])], ignore_index=True)

    if save:
        mapping_file.to_excel('/Users/murtazavahanvaty/Desktop/Mojek/pattern_matching_rules_test.xlsx', index=False)
    
    return mapping_file

def char_clean(string): 
    """
    Character cleaning function that replace a certain set of special characters with spaces
    replace all special characters except: &+@\.:
    """
    new_string = re.sub('[^a-zA-Z0-9&+@ \n\.:]', ' ', string)
    new_string = ' '.join(new_string.split())
    return new_string



def train_algorithm(matcher, mapping_file, general_rules):

    for subcategory in mapping_file.Subcategory.unique():
        for index, row in mapping_file.query(f'Subcategory == "{subcategory}"').iterrows():
            keyword = row.Keyword
            pattern = []
            for word in keyword.split(' '):
    #            Check from stop words
                pattern.append({"TEXT": {"REGEX":f"{word.lower()}.*"}})
                matcher.add(f"{subcategory}", [pattern], on_match=add_event_ent)
    for subcategory in general_rules.keys():
        for pattern in general_rules[subcategory]:
            matcher.add(f"{subcategory}", [pattern], on_match=add_event_ent)
    return matcher

def categorize_labels(narrations_df, matcher):
    narrations_df["Label"] = 0
    for index, row in narrations_df.iterrows():
        narration = row.Narration
        label = return_label(matcher, char_clean(narration).lower(), False)
        narrations_df.loc[index, "Label"] = label
    
    return narrations_df

def return_label(matcher, narration, nlp, debug=False):
    doc = nlp(narration.lower())
    matches = matcher(doc)
    if debug:
        print([token.text for token in doc])
        print(matches)
    if len(matches) > 0:
        return nlp.vocab.strings[matches[0][0]]
    else:
        return "No match"

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
    if 'error' in data.keys():
        return "Error: Can't connect to Google Search API"
    if 'items' in data.keys():
        for item in data['items']:
            if 'snippet' not in item.keys():
                continue
            snippet = item['snippet']
            doc1 = nlp(snippet.lower())
            if (len(doc1.ents) >= 1) & (type(doc1.ents) != NoneType):
                for ents in doc1.ents:
                    if ents.label_ not in labels:
                        continue
                    else:
                        # st.write(doc1)
                        keyword = [t.text for t in ents]
                        keyword = ' '.join(keyword)
                        return {"label": ents.label_, "from_google": True, "snippet": snippet, "keyword": keyword}
            else:
                continue
    else:
        {"label": 'No match', "from_google": True, "snippet": "", "keyword": ""}

def expense_tracker(nlp, narration, labels, google_api_key, search_engine_id):
    doc1 = nlp(narration.lower())
    if len(doc1.ents) >= 1:
        for doc in doc1.ents:
            label = doc.label_
            keyword = [t.text for t in doc]
            keyword = ' '.join(keyword)
            if label in labels:
                return {"label": label, "from_google": False, "snippet": "", "keyword": keyword}
            else:
                continue
        response = extract_google_query(nlp, narration, google_api_key, search_engine_id)
        return response
    else:
        label = extract_google_query(nlp, narration, google_api_key, search_engine_id)
        return label
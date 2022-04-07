import pandas as pd
import glob
import spacy
import en_core_web_sm
from spacy.matcher import Matcher
from spacy.tokens import Span
import re

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

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
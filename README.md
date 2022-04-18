# mojek

pipenv install 

python worker.py

{url}/expense-tracker?

GET request
payload = {
    "narration": "String with narration for expense tracker to categorize"
}

response = {
"from_google":boolean, >> indicates if we used google search or a rule
"keyword":string, >> this is the keyword in the narration/snippet which triggered the rule and returned the label
"label":string, >> this is the label we want returned
"narration":string, >> this is the original input
"snippet":string >> this is the output of the google search which was used to get the label
}

POST

payload = {
    "user_name": "",
    "user_email": "",
    "user_age": "",
    "user_occupation": "",
    "narration": "PCD/SPOTIFY/XXXXX",
    "user_defined_keyword": "spotify",
    "user_defined_label": "Entertainment",
    "algo_label": "Streaming",
    "from_google": false,
    "algo_keyword": "spotify",
    "snippet":  ""
}
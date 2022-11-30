from PyPDF2 import PdfFileReader
import pandas as pd
import datetime
import re
import boto3
from enum import Enum
from mojek_service.config import AWS_BUCKET_NAME, AWS_BUCKET_REGION, AWS_ACCESS_KEY, AWS_SECRET_KEY
import os

class institutions(Enum):
    KOTAK = 'Kotak'
    HDFC = 'HDFC'

class file_types(Enum):
    PDF = 'pdf'
    excel = 'excel'
    csv = 'csv'

def get_narration_dict(date, narration, amount, transaction_type, closing_balance,institution_name, censored_acc_number="", account_type="Savings"):
    return {
        "institution_name": str(institution_name.value),
        "transaction_date": date.strftime("%Y/%m/%d, %H:%M:%S"),
        "narration": narration,
        "amount": amount,
        "transaction_type": transaction_type,
        "closing_balance": float(closing_balance.replace(",","")) if type(closing_balance) == str else closing_balance,
        "apply_all": False,
        "comment": "",
        "mark_as_transfer": False,
        "hide_budget": False,
        "mark_as_duplicate": False,
        "image": "",
        "image_note":"",
        "account_info": str(institution_name.value) + " - " + account_type + " - " + censored_acc_number,
        "payment_mode": "UPI" #TODO: get payment_model NEFT, UPI etc.
        }

def get_censored_acc_number(account_number):
    return 'X'*(len(account_number) - 4) + account_number[-4:]

def kotak_format_1(pdfReader):
    """
    Aman Maroo/ Aaditya PDF
    """
    institution_name = institutions.KOTAK
    doc = []
        #Loop through each page and parse narrations
    for page_number in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(page_number)
        text = pageObj.extractText()
        if page_number == 0:
            regex = re.compile('Account # [0-9]{10}')
            acc_number_regex = regex.search(text)
            account_number = text[acc_number_regex.start(): acc_number_regex.end()][-10:]
            censored_acc_number = get_censored_acc_number(account_number)
            account_type = text[acc_number_regex.end():].split('\n')[0].strip()

        #     Matches "/n748 " [\\n] = /n  \d{1,5} = atleast 1 but no more than 5 [\\s] = blank space
        regex = re.compile('\\n\d{1,5}\\s')
        text = regex.split(text)
        #     Need to drop the first one and trim the last one
        if page_number == 0:
            text = text[2:]
        else:
            text = text[1:]
        last_element = text.pop()
        if last_element == '':
            last_element = text.pop()
        pattern = re.compile('\\nOPENING')
        r = pattern.search(last_element)
        text.append(last_element[: r.start()])
        # page_text = []
        
        for idx, sentence in enumerate(text):
            date = datetime.datetime.strptime(sentence[:20].replace('\n', ' '), '%d %b %Y %I:%M %p') #doc2
            closing_balance = float(sentence.split(' ')[-1].replace(',',''))
            amount_regex = re.compile('[+-][0-9,]+\.[0-9]{2}')
            r = amount_regex.search(sentence)
            amount = float(sentence[r.start():r.end()].replace('+','').replace(',',''))
            if amount >= 0:
                transaction_type = 'Income'
            else:
                transaction_type = 'Expense'
            narration = sentence[20:r.start()].replace('\n',"")

            doc.append(get_narration_dict(date, narration, amount, transaction_type, closing_balance,institution_name, censored_acc_number, account_type))


def kotak_format_2(pdfReader):
    """
    Ikhlaque PDF
    """
    doc = []
    institution_name = institutions.KOTAK
    #Loop through each page and parse narrations
    for page_number in range(pdfReader.numPages):
        pageObj = pdfReader.getPage(page_number)
        text = pageObj.extractText()
        if page_number == 1:
            regex = re.compile('[0-9]{12}\n')
            acc_number_regex = regex.search(text)
            account_number = text[acc_number_regex.start(): acc_number_regex.end()][:-1]
            censored_acc_number = get_censored_acc_number(account_number)
            account_type = "Savings" #TODO: No indication in statement
    return "Unsuported format, please check in later"

# parse Kotak bank PDF statement
def parse_kotak_pdf(pdf):
    # creating a pdf file object
    with open(pdf, 'rb') as pdfFileObj:
        pdfReader = PdfFileReader(pdfFileObj)
        pageObj = pdfReader.getPage(0)
        text = pageObj.extractText()
        if 'Account StatementAccount #' in text[:30]:
            doc = kotak_format_1(pdfReader)
        if 'Account No.' in text[:30]:
            doc = kotak_format_2(pdfReader)
        else:
            doc = "Unsuported format, please check in later"
    return doc

def parse_hdfc_pdf(pdf):
    with open(pdf, 'rb') as pdfFileObj:
        institution_name = institutions.HDFC
        pdfReader = PdfFileReader(pdfFileObj)
        doc = []
        old_closing_balance = 0
        ref_no_regex = re.compile('\s[a-zA-Z0-9]{15,16}\s')
        for page_number in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(page_number)
            text = pageObj.extractText()
            text = text.split('\n')
            for idx, sentence in enumerate(text):
                if 'Page No .: ' in sentence:
                    text = text[0:idx]
                elif 'STATEMENT SUMMARY :-' in sentence:
                    text = text[0:idx]
            for idx, sentence in enumerate(text):
                try:
                    #This is the start of a new narration
                    date = datetime.datetime.strptime(sentence[0:8], '%d/%m/%y')
                except:
                    #This is a continuation of an older narration and has already been handled
                    continue
                closing_balance = float(sentence.split(' ')[-1].replace(',',''))
                amount = float(sentence.split(' ')[-2].replace(',',''))
                if closing_balance <= old_closing_balance:
                    amount = -amount
                    transaction_type = 'Expense'
                else:
                    transaction_type = 'Income'
                old_closing_balance = closing_balance
                r = ref_no_regex.search(sentence)
                narration = sentence[9:r.start()]
                ref_no = sentence[r.start():r.end()]
            #     Find if next sentence is a continuation of an older narration or start of new narration
                new_index = idx+1
                new_ref_no = ref_no
                
                while (new_index < len(text)):
                    try:
                        new_date = datetime.datetime.strptime(text[new_index][0:8], '%d/%m/%y')
                        break
                    except:
                        narration += text[new_index]
                        new_index = new_index+1
                doc.append(get_narration_dict(date, narration, amount, transaction_type, closing_balance,institution_name))
    return doc

def parse_hdfc_spreadsheet(excel, file_type):
    institution_name = institutions.HDFC
    if file_type == 'csv':
        df = pd.read_csv(excel, skiprows=[i for i in range(20)])
    elif file_type == 'excel':
        df = pd.read_excel(excel, skiprows=[i for i in range(20)])
    # Drop first row
    df = df.iloc[1:,:].reset_index(drop=True)
    #Find row with Nan in all columns and drop everything after that
    selected_rows = df[df.isnull().all(axis=1)]
    df = df.iloc[0: selected_rows.index[0]]
    df.columns = ['date', 'narration','ref_no','value_date','withdrawal_amount','deposit_amount','closing_balance']
    doc = []
    for index, row in df.iterrows():
        date = datetime.datetime.strptime(row.date, '%d/%m/%y')
        narration = row.narration
        withdrawal_amount = row.withdrwal_amount
        deposit_amount = row.deposit_amount
        if pd.isnull(withdrawal_amount):
            amount = deposit_amount
            transaction_type = 'Income'
        else:
            amount = -withdrawal_amount
            transaction_type = 'Expense'
        closing_balance = row.closing_balance
        doc.append(get_narration_dict(date, narration, amount, transaction_type, closing_balance, institution_name))
    return doc

def parse_kotak_spreadsheet(file_name, file_type):
    institution_name = institutions.KOTAK
    if file_type == 'csv':
        df = pd.read_csv(file_name, skiprows=[i for i in range(12)]).iloc[:,1:-1]
        with open(file_name) as f:
            text = ''.join(f.readlines())
            regex = re.compile('Account No.,[0-9]{10}')
            account_number = text[regex.search(text).start(): regex.search(text).end()][12:]
            censored_acc_number = get_censored_acc_number(account_number)
    elif file_type == 'excel':
        df = pd.read_excel(file_name, skiprows=[i for i in range(12)]).iloc[:,1:-1]
    df.columns = ['date','value_date','narration','ref_no','amount','dr_or_cr','closing_balance']
    #Drop NA rows at the bottom
    df = df.iloc[: df[df.value_date.isna()].index[0]]
    doc=[]
    for index, row in df.iterrows():
        try:
            date = datetime.datetime.strptime(row.date, '%d-%m-%Y')
        except ValueError:
            date = datetime.datetime.strptime(row.date, '%d/%m/%y')
        narration = row.narration
        dbcr = row.dr_or_cr
        amount = float(row.amount.replace(',',""))
        if dbcr == 'CR':
            amount = amount
            transaction_type = 'Income'
        else:
            amount = -amount
            transaction_type = 'Expense'
        closing_balance = row.closing_balance
        doc.append(get_narration_dict(date, narration, amount, transaction_type, closing_balance, institution_name, censored_acc_number))
    return doc


def download_file(file_name):
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY , aws_secret_access_key=AWS_SECRET_KEY)
    with open(file_name, 'wb') as f:
        s3.download_fileobj(AWS_BUCKET_NAME, file_name, f)
    return file_name


def parse_statement(institution_name, file_type, bank_statement):
    """
    Inputs:
    institution_name: Kotak or HDFC
    file_type: excel/csv/pdf
    bank_statement: /path_to_file in cloud storage

    Response:
    Returns list of bank statement rows as dictionaries
    [
        {
            "transaction_date": date, 
            "narration": narration,
            "amount": amount,
            "transaction_name": transaction_name,
            "closing_balance": closing_balance
        },
        {

        }...
    ]

    """
    #TODO: Download bank statement from file path
    bank_statement = download_file(bank_statement)
    try:
        if institution_name == institutions.KOTAK.value:
            if file_type == file_types.PDF.value:
                doc = parse_kotak_pdf(bank_statement)
            else:
                doc = parse_kotak_spreadsheet(bank_statement, file_type)
        elif institution_name == institutions.HDFC.value:
            if file_type == file_types.PDF.value:
                doc = parse_hdfc_pdf(bank_statement)
            else:
                doc = parse_hdfc_spreadsheet(bank_statement, file_type)
    except Exception as e:
        with open('failed_statements.txt',"a+") as f:
            f.write(bank_statement)
        return {}
    # TODO: delete_file
    if os.path.exists(bank_statement):
        os.remove(bank_statement)
    return doc




from mojek_service.parse_statements import parse_statement
from mojek_service.expense_tracker import bulk_expense_tracker
from mojek_service.config import *
from mojek_service.labels import labels
import spacy
nlp = spacy.load("./mojek_pipeline")

institution_name = 'Kotak'
# institution_name = 'HDFC'
file_type = 'csv'
# file_type = 'pdf'
# pdf = '/Users/murtazavahanvaty/Downloads/BankStatement_Kotak_U1_1.pdf'
# pdf = '/Users/murtazavahanvaty/Downloads/Acct Statement_XX7415_13022022.pdf'
# pdf = 'file-1660137838925.pdf'
pdf = 'file-1660292781777.csv'
# pdf = '/Users/murtazavahanvaty/Downloads/2215163693_statement.csv'

doc = parse_statement(institution_name, file_type, pdf)
doc_w_category = bulk_expense_tracker(doc, nlp, labels, google_api_key, search_engine_id)

print(doc)



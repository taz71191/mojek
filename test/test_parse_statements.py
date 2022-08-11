from mojek_service.parse_statements import parse_statement

institution_name = 'Kotak'
# institution_name = 'HDFC'
file_type = 'csv'
# file_type = 'pdf'
# pdf = '/Users/murtazavahanvaty/Downloads/BankStatement_Kotak_U1_1.pdf'
# pdf = '/Users/murtazavahanvaty/Downloads/Acct Statement_XX7415_13022022.pdf'
# pdf = 'file-1660137838925.pdf'
# pdf = 'file-1660137911919.csv'
pdf = '/Users/murtazavahanvaty/Downloads/2215163693_statement.csv'

doc = parse_statement(institution_name, file_type, pdf)

print(doc)



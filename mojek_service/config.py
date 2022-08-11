import os

google_api_key = os.getenv("google_api_key", "")
gcp_service_account = os.getenv('gcp_service_account',"")


search_engine_id = os.getenv("search_engine_id","")
private_g_sheet_url = os.getenv("private_g_sheet_url","")


AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME","")
AWS_BUCKET_REGION = os.getenv("AWS_BUCKET_REGION","")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY","")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY","")
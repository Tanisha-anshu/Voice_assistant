import os, gspread
from dotenv import load_dotenv

load_dotenv()
gc = gspread.service_account(filename=os.getenv("GSPREAD_SERVICE_ACCOUNT_JSON"))
sh = gc.open_by_key(os.getenv("BOOKINGS_SHEET_ID"))
print("Worksheets:", sh.worksheets())

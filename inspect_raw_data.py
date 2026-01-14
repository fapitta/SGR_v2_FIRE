import pandas as pd
import os

file_path = '파이썬_SGR_데이터SET.xlsx'
if os.path.exists(file_path):
    xl = pd.ExcelFile(file_path)
    print(f"Sheets: {xl.sheet_names}")
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet, nrows=2)
        print(f"\nSheet: {sheet}")
        print(f"Columns: {df.columns.tolist()}")
else:
    print("File not found")

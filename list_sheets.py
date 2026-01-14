import pandas as pd

def list_sheets():
    file_path = '파이썬_SGR_데이터SET.xlsx'
    xl = pd.ExcelFile(file_path)
    print("Sheets available:", xl.sheet_names)

if __name__ == "__main__":
    list_sheets()

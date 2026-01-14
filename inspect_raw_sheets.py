import pandas as pd
file_path = '파이썬_SGR_데이터SET.xlsx'
xl = pd.ExcelFile(file_path)
for sheet_name in xl.sheet_names:
    print(f"\n--- Sheet: {sheet_name} ---")
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    print(df.head(10))

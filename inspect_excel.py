import pandas as pd
file = 'SGR_data.xlsx'
xl = pd.ExcelFile(file)
for sheet in xl.sheet_names:
    print(f"\n--- {sheet} ---")
    df = pd.read_excel(file, sheet_name=sheet)
    print(df.head(3))

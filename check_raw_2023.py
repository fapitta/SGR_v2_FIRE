import pandas as pd
file = 'SGR_data.xlsx'
target_year = 2023
sheets = ['상대가치변화', '연도별환산지수', '법과제도']
xl = pd.ExcelFile(file)
for s in sheets:
    if s in xl.sheet_names:
        df = pd.read_excel(file, sheet_name=s)
        # Assuming first column is year
        row = df[df.iloc[:,0] == target_year]
        print(f"\n--- {s} (Year {target_year}) ---")
        print(row)

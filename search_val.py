import pandas as pd
file = 'SGR_data.xlsx'
xl = pd.ExcelFile(file)
for sheet in xl.sheet_names:
    df = pd.read_excel(file, sheet_name=sheet)
    # Search for values near 1.0069 or 0.69
    found = df[(df == 1.0069).any(axis=1) | (df == 0.0069).any(axis=1) | (df == 0.69).any(axis=1)]
    if not found.empty:
        print(f"\n--- Found in {sheet} ---")
        print(found)

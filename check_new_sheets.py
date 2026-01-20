import pandas as pd
import json

try:
    xl = pd.ExcelFile('SGR_data.xlsx')
    sheets = xl.sheet_names
    print(f"Sheets found: {sheets}")
    
    summary = {}
    for sheet in ['num', 'contract', 'finnce']:
        if sheet in sheets:
            df = pd.read_excel('SGR_data.xlsx', sheet_name=sheet)
            summary[sheet] = {
                "columns": df.columns.tolist(),
                "head": df.head(3).to_dict()
            }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")


import pandas as pd
import os

def list_all_sheet_columns():
    file_path = "SGR_data.xlsx"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    try:
        with pd.ExcelFile(file_path) as xls:
            print(f"Sheet names: {xls.sheet_names}")
            for sheet in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet, nrows=5)
                print(f"\n[Sheet: {sheet}]")
                print(f"Columns: {df.columns.tolist()}")
                
    except Exception as e:
        print(f"Error reading excel: {e}")

if __name__ == "__main__":
    list_all_sheet_columns()

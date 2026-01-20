import pandas as pd
import os

file_path = "SGR_data.xlsx"
try:
    df = pd.read_excel(file_path, sheet_name='contract')
    print("Columns:", df.columns.tolist())
    print("\nFirst 5 rows:")
    print(df.head())
    
    # Check for specific columns
    if '수가인상율_전체' in df.columns:
        print("\n'수가인상율_전체' found.")
    else:
        print("\n'수가인상율_전체' NOT found.")
        
    if '추가소요재정_전체' in df.columns:
        print("'추가소요재정_전체' found.")
    else:
        print("'추가소요재정_전체' NOT found.")

except Exception as e:
    print(f"Error: {e}")

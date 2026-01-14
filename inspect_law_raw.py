import pandas as pd

def inspect_law_excel_raw():
    df = pd.read_excel('파이썬_SGR_데이터SET.xlsx', sheet_name='법과제도')
    print("=== Column Names ===")
    print(df.columns.tolist())
    print("\n=== First 5 rows ===")
    print(df.head())

if __name__ == "__main__":
    inspect_law_excel_raw()

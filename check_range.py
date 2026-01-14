from 파이썬용_sgr_2027 import DataProcessor
import pandas as pd

def check_data_range():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    data = processor.raw_data
    
    print("=== Data Range Check ===")
    for key, df in data.items():
        if isinstance(df, pd.DataFrame):
            print(f"\n[{key}] Index Range: {df.index.min()} ~ {df.index.max()}")
            print(f"Columns: {df.columns.tolist()[:5]} ...")
            if 'df_expenditure' in key:
                print(df.head())

if __name__ == "__main__":
    check_data_range()

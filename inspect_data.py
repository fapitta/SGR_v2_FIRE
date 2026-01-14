from 파이썬용_sgr_2027 import DataProcessor
import pandas as pd

def inspect_reval_data():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    df = processor.raw_data['df_sgr_reval']
    
    print("=== 환산지수 데이터 (df_sgr_reval) ===")
    print("Columns:", df.columns.tolist())
    print("\n2019-2021 Data:")
    print(df.loc[2019:2021])

if __name__ == "__main__":
    inspect_reval_data()

from 파이썬용_sgr_2027 import DataProcessor
import pandas as pd

def inspect_mapping_and_data():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    data = processor.raw_data
    
    print("=== [1] Expenditure Columns (진료비_실제) ===")
    print(data['df_expenditure'].columns.tolist())
    
    print("\n=== [2] MEI Weights Index (종별비용구조) ===")
    print(data['df_weights'].index.tolist())
    
    print("\n=== [3] Law Change Columns (법과제도) ===")
    print(data['df_sgr_law'].columns.tolist())
    
    print("\n=== [4] Reval (Applied CF) Columns (연도별환산지수) ===")
    print(data['df_sgr_reval'].columns.tolist())

    print("\n=== [5] MEI Weights Data View ===")
    print(data['df_weights'])

if __name__ == "__main__":
    inspect_mapping_and_data()

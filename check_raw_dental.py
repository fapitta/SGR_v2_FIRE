from 파이썬용_sgr_2027 import DataProcessor
import pandas as pd

def check_dental_law_raw():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    law = processor.raw_data['df_sgr_law']
    reval = processor.raw_data['df_sgr_reval']
    
    print("=== [Law Indices - Dental] ===")
    cols = ['치과병원', '치과의원', '한방병원', '한의원']
    print(law[cols].loc[2014:2025])
    
    print("\n=== [Reval - Dental] ===")
    print(reval[cols].loc[2014:2025])

if __name__ == "__main__":
    check_dental_law_raw()

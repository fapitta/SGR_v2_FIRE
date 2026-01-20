import sys
import os
import pandas as pd

# Load the DataProcessor from the main app file
from 파이썬용_sgr_2027 import DataProcessor

def debug_data_values():
    dp = DataProcessor('SGR_data.xlsx')
    df_exp = dp.raw_data['df_expenditure']
    df_law = dp.raw_data['df_sgr_law']
    
    hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    
    print("=== Law Index Values (Targeting 10 Types) ===")
    print(df_law[hospital_types].loc[2020:2025])
    
    print("\n=== Expenditure Values (Targeting 10 Types) ===")
    print(df_exp[hospital_types].loc[2020:2025])
    
    # Calculate Weighted Average using the app's data
    results = []
    for year in range(2014, 2026):
        if year in df_exp.index and year in df_law.index:
            exp_y = df_exp.loc[year, hospital_types]
            law_y = df_law.loc[year, hospital_types]
            
            total_exp = exp_y.sum()
            if total_exp > 0:
                weighted_avg = (exp_y * law_y).sum() / total_exp
                results.append({
                    '연도': year,
                    '가중평균_법과제도': weighted_avg,
                    '총진료비': total_exp
                })
    
    print("\n=== Calculated Weighted Average Results ===")
    res_df = pd.DataFrame(results)
    print(res_df)

if __name__ == "__main__":
    debug_data_values()

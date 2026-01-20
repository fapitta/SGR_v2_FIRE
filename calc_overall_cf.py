import pandas as pd
import numpy as np
import os
from openpyxl import load_workbook

# Constants matching the main application
HOSPITAL_TYPES = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']

def load_data():
    file_path = r'h:\병원환산지수연구_2027년\SGR앱개발_v2\SGR_data.xlsx'
    if not os.path.exists(file_path):
        return None, None
    
    # Load expenditure (Revenue)
    df_exp = pd.read_excel(file_path, sheet_name='expenditure_real', index_col=0)
    df_exp.index = pd.to_numeric(df_exp.index, errors='coerce')
    df_exp = df_exp[df_exp.index.notnull()].astype(float)
    
    # Load Conversion Factors (CF)
    df_cf = pd.read_excel(file_path, sheet_name='cf_t', index_col=0)
    df_cf.index = pd.to_numeric(df_cf.index, errors='coerce')
    df_cf = df_cf[df_cf.index.notnull()].astype(float)
    
    return df_exp, df_cf

def calculate_overall_cf():
    df_exp, df_cf = load_data()
    if df_exp is None or df_cf is None:
        print("Error: Could not load data.")
        return
    
    # Get common years
    common_years = sorted(list(set(df_exp.index) & set(df_cf.index)))
    
    results = []
    for year in common_years:
        if year < 2010 or year > 2028: continue
        
        # Get data for the year
        rev = df_exp.loc[year, HOSPITAL_TYPES].fillna(0)
        cf = df_cf.loc[year, HOSPITAL_TYPES].fillna(0)
        
        total_rev = rev.sum()
        if total_rev > 0:
            # Weighted Average
            overall_cf = (rev * cf).sum() / total_rev
            results.append({'연도': int(year), '전체_환산지수': overall_cf})
    
    return pd.DataFrame(results)

df_result = calculate_overall_cf()
if df_result is not None:
    print(df_result.to_string(index=False))

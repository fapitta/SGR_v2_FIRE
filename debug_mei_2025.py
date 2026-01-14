
import pandas as pd
import numpy as np
import os

# Load data similarly to the app
file_path = 'SGR_data.xlsx'
hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']

def load_sheet(name, filter_years=False):
    df = pd.read_excel(file_path, sheet_name=name)
    if filter_years:
        col = '연도' if '연도' in df.columns else df.columns[0]
        df = df.set_index(col)
        df.index = pd.to_numeric(df.index, errors='coerce')
        df = df[df.index.notna()].astype(int)
    else:
        df = df.set_index(df.columns[0])
    return df

df_inf = load_sheet('factor_pd', filter_years=True)
df_weights = load_sheet('cost_structure').T # Transpose as in app

target_year = 2025
calc_year = target_year - 2 # 2023

# Labor Rates (3 year avg)
base_year = calc_year - 3 # 2020
I_types = [c for c in df_inf.columns if '인건비' in c]
labor_rates = (df_inf.loc[calc_year, I_types] / df_inf.loc[base_year, I_types])**(1/3)

# Non-Labor Rates (1 year)
non_I_types = [c for c in df_inf.columns if '관리비' in c or '재료비' in c]
raw_rates = df_inf.loc[calc_year, non_I_types] / df_inf.loc[calc_year-1, non_I_types]

print(f"--- 2025년 MEI 산출 기초 수치 (T-2 = {calc_year}년 데이터 기준) ---")
print(f"\n[1] 인건비 증가율 (2020->2023 3년 연평균):")
for i, v in labor_rates.items():
    print(f"  {i}: {v:.6f}")

print(f"\n[2] 관리비/재료비 증가율 (2022->2023 1년):")
for i, v in raw_rates.items():
    print(f"  {i}: {v:.6f}")

print(f"\n[3] 종별 가중치 (Weights):")
print(df_weights)

print(f"\n[4] 시나리오 I1M1Z1 상세 계산 과정:")
i_col = '인건비_1'
m_col = '관리비_1'
z_col = '재료비_1'

l_rate = labor_rates[i_col]
m_rate = raw_rates[m_col]
z_rate = raw_rates[z_col]

results = []
for t in hospital_types:
    w_l = df_weights.loc[t, '인건비']
    w_m = df_weights.loc[t, '관리비']
    w_z = df_weights.loc[t, '재료비']
    
    mei = (w_l * l_rate) + (w_m * m_rate) + (w_z * z_rate)
    results.append({
        '종별': t,
        'W_인건비': f"{w_l:.4f}",
        'W_관리비': f"{w_m:.4f}",
        'W_재료비': f"{w_z:.4f}",
        'L_Rate': f"{l_rate:.6f}",
        'M_Rate': f"{m_rate:.6f}",
        'Z_Rate': f"{z_rate:.6f}",
        '계산식': f"({w_l:.4f}*{l_rate:.4f}) + ({w_m:.4f}*{m_rate:.4f}) + ({w_z:.4f}*{z_rate:.4f})",
        'MEI_Index': f"{mei:.6f}",
        'MEI_%': f"{(mei-1)*100:.4f}%"
    })

df_res = pd.DataFrame(results)
print(df_res.to_string(index=False))

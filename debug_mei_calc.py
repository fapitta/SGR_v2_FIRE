import pandas as pd
import numpy as np

def explain_calculation():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    TARGET_YEAR = 2025 # T=2025, so T-2=2023
    
    # 1. 가중치 로드
    df_weights = pd.read_excel(EXCEL_FILE_PATH, sheet_name='종별비용구조', index_col=0).T
    weights = df_weights.loc['상급종합']
    
    # 2. 물가지수 로드
    df_inf = pd.read_excel(EXCEL_FILE_PATH, sheet_name='생산요소_물가', index_col=0)
    # 인덱스 정리 (float to int if target_year)
    df_inf.index = [int(i) if isinstance(i, (int, float)) else i for i in df_inf.index]
    
    print("--- [1] 상급종합병원 비용 가중치 ---")
    print(weights)
    
    print("\n--- [2] 인건비 (I1) 계산 (3개년 연평균 증가율) ---")
    year_T = 2023
    year_T_3 = 2020
    val_T = df_inf.loc[year_T, '인건비_1']
    val_T_3 = df_inf.loc[year_T_3, '인건비_1']
    labor_rate = (val_T / val_T_3) ** (1/3)
    print(f"2023년 지수: {val_T}")
    print(f"2020년 지수: {val_T_3}")
    print(f"I1 = ({val_T} / {val_T_3})^(1/3) = {labor_rate}")
    
    print("\n--- [3] 관리비 (M1) 계산 (T-2년 전년대비 증가율) ---")
    val_M_2023 = df_inf.loc[2023, '관리비_1']
    val_M_2022 = df_inf.loc[2022, '관리비_1']
    m_rate = val_M_2023 / val_M_2022
    print(f"2023년 지수: {val_M_2023}")
    print(f"2022년 지수: {val_M_2022}")
    print(f"M1 = {val_M_2023} / {val_M_2022} = {m_rate}")
    
    print("\n--- [4] 재료비 (Z1) 계산 (T-2년 전년대비 증가율) ---")
    val_Z_2023 = df_inf.loc[2023, '재료비_1']
    val_Z_2022 = df_inf.loc[2022, '재료비_1']
    z_rate = val_Z_2023 / val_Z_2022
    print(f"2023년 지수: {val_Z_2023}")
    print(f"2022년 지수: {val_Z_2022}")
    print(f"Z1 = {val_Z_2023} / {val_Z_2022} = {z_rate}")
    
    print("\n--- [5] 최종 MEI (I1M1Z1) 계산 ---")
    mei = (weights['인건비'] * labor_rate + 
           weights['관리비'] * m_rate + 
           weights['재료비'] * z_rate)
    print(f"Formula: (W_I * I1) + (W_M * M1) + (W_Z * Z1)")
    print(f"MEI = ({weights['인건비']} * {labor_rate}) + ({weights['관리비']} * {m_rate}) + ({weights['재료비']} * {z_rate})")
    print(f"MEI Index: {mei}")
    print(f"MEI Rate (%): {(mei - 1) * 100}")

if __name__ == "__main__":
    explain_calculation()

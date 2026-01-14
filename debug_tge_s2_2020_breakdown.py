import pandas as pd
import numpy as np

def explain_tge_s2_2020_tertiary():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    
    # 1. 기초 데이터 로드
    df_gdp_pop = pd.read_excel(EXCEL_FILE_PATH, sheet_name='1인당GDP', index_col=0)
    df_nhi_pop = pd.read_excel(EXCEL_FILE_PATH, sheet_name='건보대상', index_col=0)
    df_reval = pd.read_excel(EXCEL_FILE_PATH, sheet_name='연도별환산지수', index_col=0)
    df_law = pd.read_excel(EXCEL_FILE_PATH, sheet_name='법과제도', index_col=0)
    df_ae = pd.read_excel(EXCEL_FILE_PATH, sheet_name='진료비_실제', index_col=0)
    
    year_t = 2020
    year_t_1 = 2019
    
    # --- SGR (S2) 구성요소 산출 ---
    
    # A. 1인당 실질 GDP 지수 (S2)
    # S1 지수 선출
    gdp_t = df_gdp_pop.loc[year_t, '실질GDP']
    pop_gdp_t = df_gdp_pop.loc[year_t, '영안인구']
    gdp_t_1 = df_gdp_pop.loc[year_t_1, '실질GDP']
    pop_gdp_t_1 = df_gdp_pop.loc[year_t_1, '영안인구']
    
    gdp_per_capita_t = gdp_t / pop_gdp_t
    gdp_per_capita_t_1 = gdp_t_1 / pop_gdp_t_1
    gdp_idx_s1 = gdp_per_capita_t / gdp_per_capita_t_1
    
    # S2 약속: 1 + (S1 - 1) * 0.8
    gdp_idx_s2 = 1 + (gdp_idx_s1 - 1) * 0.8
    
    # B. 인구 지수 (S2)
    # S2 약속: t년 고령화 반영 인구 / t-1년 순수 대상자수
    pop_s2_weighted_t = df_nhi_pop.loc[year_t, '건보_고령화반영후(대상자수)']
    pop_s1_raw_t_1 = df_nhi_pop.loc[year_t_1, '건보대상자수']
    pop_idx_s2 = pop_s2_weighted_t / pop_s1_raw_t_1
    
    # C. 법과제도 및 환산지수 지수
    law_idx = df_law.loc[year_t, '상급종합']
    reval_t = df_reval.loc[year_t, '상급종합']
    reval_t_1 = df_reval.loc[year_t_1, '상급종합']
    reval_idx = reval_t / reval_t_1
    
    # D. 최종 SGR (S2) 지수
    sgr_s2 = gdp_idx_s2 * pop_idx_s2 * law_idx * reval_idx
    
    # --- TGE (S2) 산출 ---
    # TGE_t = AE_{t-1} * SGR_S2_t
    ae_2019 = df_ae.loc[2019, '상급종합']
    tge_2020 = ae_2019 * sgr_s2
    
    print(f"=== [2020년 상급종합병원 TGE (S2) 상세 산출 과정] ===")
    print(f"\n1. SGR 구성요소 (S2 약속 로직)")
    print(f"  - 1인당 GDP 지수 (S1): {gdp_idx_s1:.6f}")
    print(f"  - 1인당 GDP 지수 (S2): 1 + ({gdp_idx_s1:.6f} - 1) * 0.8 = {gdp_idx_s2:.6f}")
    print(f"  - 인구 지수 (S2): {pop_s2_weighted_t:,.0f} (20년 고령화인구) / {pop_s1_raw_t_1:,.0f} (19년 순수인구) = {pop_idx_s2:.6f}")
    print(f"  - 법제도 지수: {law_idx:.6f}")
    print(f"  - 환산지수 지수: {reval_t} / {reval_t_1} = {reval_idx:.6f}")
    print(f"  - 최종 SGR (S2): {gdp_idx_s2:.6f} * {pop_idx_s2:.6f} * {law_idx:.6f} * {reval_idx:.6f} = {sgr_s2:.6f}")
    
    print(f"\n2. TGE 산출 (목표 진료비)")
    print(f"  - 2019년 실제 진료비 (AE): {ae_2019:,.2f} 억 원")
    print(f"  - 2020년 목표 진료비 (TGE): {ae_2019:,.2f} * {sgr_s2:.6f} = {tge_2020:,.2f} 억 원")

if __name__ == "__main__":
    explain_tge_s2_2020_tertiary()

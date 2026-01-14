import pandas as pd
import numpy as np

def debug_sgr_2015():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    
    # 데이터 로드
    df_gdp_pop_raw = pd.read_excel(EXCEL_FILE_PATH, sheet_name='1인당GDP', index_col=0)
    df_건보 = pd.read_excel(EXCEL_FILE_PATH, sheet_name='건보대상', index_col=0)
    df_reval = pd.read_excel(EXCEL_FILE_PATH, sheet_name='연도별환산지수', index_col=0)
    df_law = pd.read_excel(EXCEL_FILE_PATH, sheet_name='법과제도', index_col=0)
    
    year_t = 2015
    year_t_1 = 2014
    
    # 1. 1인당 GDP 지수
    gdp_t = df_gdp_pop_raw.loc[year_t, '실질GDP']
    pop_t_gdp = df_gdp_pop_raw.loc[year_t, '영안인구']
    gdp_t_1 = df_gdp_pop_raw.loc[year_t_1, '실질GDP']
    pop_t_1_gdp = df_gdp_pop_raw.loc[year_t_1, '영안인구']
    
    gdp_per_capita_t = gdp_t / pop_t_gdp
    gdp_per_capita_t_1 = gdp_t_1 / pop_t_1_gdp
    gdp_idx = gdp_per_capita_t / gdp_per_capita_t_1
    
    # 2. 인구 지수
    pop_s1_t = df_건보.loc[year_t, '건보대상자수']
    pop_s1_t_1 = df_건보.loc[year_t_1, '건보대상자수']
    pop_idx_s1 = pop_s1_t / pop_s1_t_1
    
    # 고령화 반영 지수 (S2) - 현재 코드 로직 확인용
    pop_s2_weighted_t = df_건보.loc[year_t, '건보_고령화반영후(대상자수)']
    pop_idx_s2_current = pop_s2_weighted_t / pop_s1_t
    
    # 3. 법과제도 지수
    law_idx = df_law.loc[year_t, '상급종합']
    
    # 4. 환산지수 지수
    reval_t = df_reval.loc[year_t, '상급종합']
    reval_t_1 = df_reval.loc[year_t_1, '상급종합']
    reval_idx = reval_t / reval_t_1
    
    print(f"--- 2015년 상급종합 SGR 구성요소 상세 ---")
    print(f"1. 1인당 GDP 지수: {gdp_idx:.6f} ({gdp_per_capita_t:.2f} / {gdp_per_capita_t_1:.2f})")
    print(f"2. 인구 지수 (S1): {pop_idx_s1:.6f} ({pop_s1_t} / {pop_s1_t_1})")
    print(f"3. 인구 지수 (S2, 현재로직): {pop_idx_s2_current:.6f} ({pop_s2_weighted_t} / {pop_s1_t})")
    print(f"4. 법과제도 지수: {law_idx:.6f}")
    print(f"5. 환산지수 지수: {reval_idx:.6f} ({reval_t} / {reval_t_1})")
    
    sgr_s1 = pop_idx_s1 * gdp_idx * law_idx * reval_idx
    sgr_s2 = pop_idx_s2_current * gdp_idx * law_idx * reval_idx
    
    print(f"\n[결과]")
    print(f"SGR S1 = {pop_idx_s1:.6f} * {gdp_idx:.6f} * {law_idx:.6f} * {reval_idx:.6f} = {sgr_s1:.6f}")
    print(f"SGR S2 = {pop_idx_s2_current:.6f} * {gdp_idx:.6f} * {law_idx:.6f} * {reval_idx:.6f} = {sgr_s2:.6f}")

if __name__ == "__main__":
    debug_sgr_2015()

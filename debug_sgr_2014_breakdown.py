import pandas as pd
import numpy as np

def explain_sgr_2014_tertiary():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    
    # 데이터 로드
    df_gdp_pop = pd.read_excel(EXCEL_FILE_PATH, sheet_name='1인당GDP', index_col=0)
    df_nhi_pop = pd.read_excel(EXCEL_FILE_PATH, sheet_name='건보대상', index_col=0)
    df_reval = pd.read_excel(EXCEL_FILE_PATH, sheet_name='연도별환산지수', index_col=0)
    df_law = pd.read_excel(EXCEL_FILE_PATH, sheet_name='법과제도', index_col=0)
    
    year_t = 2014
    year_t_1 = 2013
    
    # 1. 1인당 실질 GDP 지수 (S1)
    gdp_t = df_gdp_pop.loc[year_t, '실질GDP']
    pop_gdp_t = df_gdp_pop.loc[year_t, '영안인구']
    gdp_t_1 = df_gdp_pop.loc[year_t_1, '실질GDP']
    pop_gdp_t_1 = df_gdp_pop.loc[year_t_1, '영안인구']
    
    gdp_per_capita_t = gdp_t / pop_gdp_t
    gdp_per_capita_t_1 = gdp_t_1 / pop_gdp_t_1
    gdp_idx = gdp_per_capita_t / gdp_per_capita_t_1
    
    # 2. 인구 지수 (S1)
    pop_nhi_t = df_nhi_pop.loc[year_t, '건보대상자수']
    pop_nhi_t_1 = df_nhi_pop.loc[year_t_1, '건보대상자수']
    pop_idx = pop_nhi_t / pop_nhi_t_1
    
    # 3. 법과제도 지수
    law_idx = df_law.loc[year_t, '상급종합']
    
    # 4. 환산지수 지수
    reval_t = df_reval.loc[year_t, '상급종합']
    reval_t_1 = df_reval.loc[year_t_1, '상급종합']
    reval_idx = reval_t / reval_t_1
    
    # 최종 SGR
    sgr_s1 = gdp_idx * pop_idx * law_idx * reval_idx
    
    print(f"--- [2014년 상급종합병원 SGR (S1) 상세 산출 과정] ---")
    print(f"\n1. 1인당 실질 GDP 지수 (S1)")
    print(f"  - 2014년 1인당 GDP: {gdp_t} / {pop_gdp_t} = {gdp_per_capita_t:.6f}")
    print(f"  - 2013년 1인당 GDP: {gdp_t_1} / {pop_gdp_t_1} = {gdp_per_capita_t_1:.6f}")
    print(f"  - GDP 지수 = {gdp_per_capita_t:.6f} / {gdp_per_capita_t_1:.6f} = {gdp_idx:.6f}")
    
    print(f"\n2. 인구 지수 (S1)")
    print(f"  - 2014년 건보대상자수: {pop_nhi_t}")
    print(f"  - 2013년 건보대상자수: {pop_nhi_t_1}")
    print(f"  - 인구 지수 = {pop_nhi_t} / {pop_nhi_t_1} = {pop_idx:.6f}")
    
    print(f"\n3. 법과제도 지수")
    print(f"  - 2014년 상급종합 법제도 변화율: {law_idx:.6f}")
    
    print(f"\n4. 환산지수 지수")
    print(f"  - 2014년 환산지수: {reval_t}")
    print(f"  - 2013년 환산지수: {reval_t_1}")
    print(f"  - 환산지수 지수 = {reval_t} / {reval_t_1} = {reval_idx:.6f}")
    
    print(f"\n5. 최종 SGR (S1) 산출")
    print(f"  - 공식: GDP지수 * 인구지수 * 법제도지수 * 환산지수지수")
    print(f"  - 계산: {gdp_idx:.6f} * {pop_idx:.6f} * {law_idx:.6f} * {reval_idx:.6f} = {sgr_s1:.6f}")

if __name__ == "__main__":
    explain_sgr_2014_tertiary()

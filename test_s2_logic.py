import pandas as pd
import numpy as np

def test_s2_logic():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    xl = pd.ExcelFile(EXCEL_FILE_PATH)
    df_gdp = pd.read_excel(xl, sheet_name='1인당GDP', index_col=0)
    df_pop = pd.read_excel(xl, sheet_name='건보대상', index_col=0)
    
    year_t = 2015
    
    # --- Population ---
    pop_s1_idx = df_pop.loc[year_t, '건보대상자수'] / df_pop.loc[year_t-1, '건보대상자수']
    pop_s2_idx = df_pop.loc[year_t, '건보_고령화반영후(대상자수)'] / df_pop.loc[year_t-1, '건보_고령화반영후(대상자수)']
    
    # --- GDP ---
    def get_gdp_growth(t):
        return (df_gdp.loc[t, '실질GDP']/df_gdp.loc[t, '영안인구']) / (df_gdp.loc[t-1, '실질GDP']/df_gdp.loc[t-1, '영안인구'])

    gdp_s1_idx = get_gdp_growth(year_t)
    
    # GDP S2: 10-year CAGR? (t / t-10)^(1/10)
    gdp_s2_idx = ((df_gdp.loc[year_t, '실질GDP']/df_gdp.loc[year_t, '영안인구']) / 
                  (df_gdp.loc[year_t-10, '실질GDP']/df_gdp.loc[year_t-10, '영안인구'])) ** (1/10)
    
    print(f"Year: {year_t}")
    print(f"Pop S1 Index: {pop_s1_idx:.6f}")
    print(f"Pop S2 Index: {pop_s2_idx:.6f}")
    print(f"GDP S1 Index: {gdp_s1_idx:.6f}")
    print(f"GDP S2 Index: {gdp_s2_idx:.6f}")

if __name__ == "__main__":
    test_s2_logic()

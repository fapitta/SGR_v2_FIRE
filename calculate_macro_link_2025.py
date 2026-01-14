import pandas as pd
import numpy as np

# 1. Data Loader
def load_data():
    file_path = '파이썬_SGR_데이터SET.xlsx'
    xl = pd.ExcelFile(file_path)
    
    df_mei_raw = pd.read_excel(file_path, sheet_name='생산요소_물가', index_col=0)
    df_weights = pd.read_excel(file_path, sheet_name='종별비용구조', index_col=0).T
    df_gdp = pd.read_excel(file_path, sheet_name='1인당GDP', index_col=0)
    df_rv = pd.read_excel(file_path, sheet_name='상대가치변화', index_col=0)
    df_exp = pd.read_excel(file_path, sheet_name='진료비_실제', index_col=0)
    
    GROUP_MAPPING = {
        '병원': ['상급종합', '종합병원', '병원', '요양병원'],
        '의원': ['의원'],
        '치과': ['치과병원', '치과의원'],
        '한방': ['한방병원', '한의원'],
        '약국': ['약국']
    }
    
    return {
        'df_mei_raw': df_mei_raw,
        'df_weights': df_weights,
        'df_gdp': df_gdp,
        'df_rv': df_rv,
        'df_exp': df_exp,
        'GROUP_MAPPING': GROUP_MAPPING
    }

# 2. MEI Scenarios Calculation
def calculate_mei_16(data, year):
    df_inf = data['df_mei_raw']
    df_weights = data['df_weights']
    
    # Labor rate: (year / year-3)**(1/3)
    I_types = [col for col in df_inf.columns if '인건비' in col]
    labor_rates = (df_inf.loc[year, I_types] / df_inf.loc[year-3, I_types]) ** (1/3) - 1
    
    # Raw rates: (year / year-1) - 1
    M_types = [col for col in df_inf.columns if '관리비' in col]
    Z_types = [col for col in df_inf.columns if '재료비' in col]
    raw_rates = df_inf.loc[year] / df_inf.loc[year-1] - 1
    
    mei_results = {}
    for i_col in I_types:
        val_i = labor_rates[i_col]
        for m_col in M_types:
            val_m = raw_rates[m_col]
            for z_col in Z_types:
                val_z = raw_rates[z_col]
                
                name = f"I{i_col.split('_')[-1]}M{m_col.split('_')[-1]}Z{z_col.split('_')[-1]}"
                mei_idx = (
                    df_weights['인건비'] * val_i +
                    df_weights['관리비'] * val_m +
                    df_weights['재료비'] * val_z
                )
                mei_results[name] = mei_idx
                
    df_mei = pd.DataFrame(mei_results)
    df_stats = pd.DataFrame({
        '평균': df_mei.mean(axis=1),
        '최대': df_mei.max(axis=1),
        '최소': df_mei.min(axis=1),
        '중위수': df_mei.median(axis=1)
    })
    return pd.concat([df_mei, df_stats], axis=1)

# 3. Linked Model Calculation
def calculate_linked_model_2025():
    data = load_data()
    TARGET_YEAR = 2025
    DATA_YEAR = 2023
    
    # 1. GDP Growth Rate 2023
    gdp_2023 = data['df_gdp'].loc[2023, '실질GDP']
    gdp_2022 = data['df_gdp'].loc[2022, '실질GDP']
    gdp_rate = (gdp_2023 / gdp_2022) - 1
    
    # 2. MEI Growths 2023 (16 scenarios)
    df_mei_growth = calculate_mei_16(data, DATA_YEAR)
    
    # 3. Base Rate using Formula
    # Formula: if g > m: g / else: g + 1/3(m-g)
    def link_formula(m):
        if gdp_rate > m:
            return gdp_rate
        else:
            return gdp_rate + (1/3 * (m - gdp_rate))
            
    df_base_rate = df_mei_growth.applymap(link_formula)
    
    # 4. RV Adjustment
    try:
        rv_rate = data['df_rv'].loc[DATA_YEAR] - 1
    except:
        rv_rate = 0
        
    df_cf_10 = (df_base_rate.subtract(rv_rate, axis=0)) * 100
    
    # 5. Type Grouping (5 types)
    exp_weights = data['df_exp'].loc[DATA_YEAR]
    type_results = {}
    for group, members in data['GROUP_MAPPING'].items():
        valid_members = [m for m in members if m in df_cf_10.index and m in exp_weights.index]
        if not valid_members: continue
        w = exp_weights.loc[valid_members] / exp_weights.loc[valid_members].sum()
        type_results[group] = df_cf_10.loc[valid_members].mul(w, axis=0).sum(axis=0)
        
    df_cf_5 = pd.DataFrame(type_results).T
    
    return gdp_rate, df_mei_growth, df_cf_10, df_cf_5

if __name__ == "__main__":
    g_rate, df_mei, df_10, df_5 = calculate_linked_model_2025()
    
    print(f"--- [거시지표연계모형 검증: CF_2025] ---")
    print(f"1. 2023년 실질 GDP 증가율: {g_rate*100:.2f}%")
    print(f"\n2. [종별] 2025년 조정률 (MEI_평균 시나리오 적용)")
    print(df_10['평균'].round(2))
    
    print(f"\n3. [유형별] 2025년 조정률 (MEI_평균 시나리오 적용)")
    print(df_5['평균'].round(2))
    
    # Save all 16 scenarios to Excel
    with pd.ExcelWriter('거시지표연계모형_CF2025_16시나리오.xlsx') as writer:
        df_10.to_excel(writer, sheet_name='10개_종별_조정률')
        df_5.to_excel(writer, sheet_name='5개_유형별_조정률')
    
    print(f"\n✅ 16개 시나리오 상세 결과가 '거시지표연계모형_CF2025_16시나리오.xlsx'에 저장되었습니다.")

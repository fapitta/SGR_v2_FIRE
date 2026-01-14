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
    
    try:
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
    except Exception as e:
        return None

# 3. Main Calculation Logic
def run_linked_model_full():
    data = load_data()
    TARGET_YEARS = range(2020, 2028)
    
    CATEGORIES_10 = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    TYPES_5 = ['병원', '의원', '치과', '한방', '약국']
    
    all_res_10 = []
    all_res_5 = []
    
    for ty in TARGET_YEARS:
        dy = ty - 2
        
        # 1. GDP Growth
        try:
            gdp_rate = (data['df_gdp'].loc[dy, '실질GDP'] / data['df_gdp'].loc[dy-1, '실질GDP']) - 1
        except:
            continue
            
        # 2. MEI 16 Scenarios
        df_mei = calculate_mei_16(data, dy)
        if df_mei is None: continue
        
        # 3. Formula: GDP+1/3(MEI-GDP) if MEI > GDP else GDP
        def link_formula(m):
            return gdp_rate + (1/3 * (m - gdp_rate)) if m > gdp_rate else gdp_rate
            
        df_base = df_mei.map(link_formula)
        
        # 4. RV Adj
        try:
            rv_rate = data['df_rv'].loc[dy] - 1
            # Filter valid types
            rv_rate = rv_rate.reindex(df_mei.index)
        except:
            rv_rate = 0
            
        df_cf_10_all = (df_base.subtract(rv_rate, axis=0)) * 100
        df_cf_10 = df_cf_10_all.reindex(CATEGORIES_10)
        
        # Save 10 categories
        tmp_10 = df_cf_10.copy()
        tmp_10['연도'] = ty
        all_res_10.append(tmp_10.reset_index().rename(columns={'index': '종별'}))
        
        # 5. Type Grouping
        try:
            exp_w = data['df_exp'].loc[dy]
        except: continue
        
        type_res = {}
        for group in TYPES_5:
            members = data['GROUP_MAPPING'][group]
            valid = [m for m in members if m in df_cf_10_all.index and m in exp_w.index]
            if not valid: continue
            
            w = exp_w.loc[valid] / exp_w.loc[valid].sum()
            type_res[group] = df_cf_10_all.loc[valid].mul(w, axis=0).sum(axis=0)
            
        df_cf_5 = pd.DataFrame(type_res).T.reindex(TYPES_5)
        tmp_5 = df_cf_5.copy()
        tmp_5['연도'] = ty
        all_res_5.append(tmp_5.reset_index().rename(columns={'index': '유형'}))
        
    # Combine
    df_final_10 = pd.concat(all_res_10, ignore_index=True)
    df_final_5 = pd.concat(all_res_5, ignore_index=True)
    
    # Reorder columns
    cols_10 = ['연도', '종별'] + [c for c in df_final_10.columns if c not in ['연도', '종별']]
    cols_5 = ['연도', '유형'] + [c for c in df_final_5.columns if c not in ['연도', '유형']]
    
    return df_final_10[cols_10], df_final_5[cols_5]

if __name__ == "__main__":
    df10, df5 = run_linked_model_full()
    
    with pd.ExcelWriter('거시지표연계모형_CF_2020_2027.xlsx') as writer:
        df10.to_excel(writer, sheet_name='10개_종별_조정률', index=False)
        df5.to_excel(writer, sheet_name='5개_유형별_조정률', index=False)
        
    print("✅ 거시지표 연계 모형 (2020~2027) 산출 완료.")
    print("\n--- [5개 유형별 평균 시나리오 추이 (%)] ---")
    trend_5 = df5.pivot(index='연도', columns='유형', values='평균')
    print(trend_5.round(2))
    
    print("\n--- [10개 종별 평균 시나리오 추이 (%)] ---")
    trend_10 = df10.pivot(index='연도', columns='종별', values='평균')
    print(trend_10.round(2))

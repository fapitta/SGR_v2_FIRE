import pandas as pd
import numpy as np
import os

# 1. Data Loading and Preprocessing
class DataProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.GROUP_MAPPING = {
            '병원': ['상급종합', '종합병원', '병원', '요양병원'],
            '의원': ['의원'],
            '치과': ['치과병원', '치과의원'],
            '한방': ['한방병원', '한의원'],
            '약국': ['약국']
        }
    
    def _load_sheet(self, sheet_name, index_col=0):
        df = pd.read_excel(self.file_path, sheet_name=sheet_name, index_col=index_col)
        if isinstance(df.index, pd.Index):
            df.index = [int(i) if isinstance(i, (int, float)) and not pd.isna(i) else i for i in df.index]
        df.columns = [int(c) if isinstance(c, (int, float)) and not pd.isna(c) else c for c in df.columns]
        return df.apply(pd.to_numeric, errors='coerce')

    def load_all_data(self):
        df_expenditure = self._load_sheet('진료비_실제')
        df_weights = self._load_sheet('종별비용구조').T
        df_raw_mei_inf = self._load_sheet('생산요소_물가')
        df_rel_value = self._load_sheet('상대가치변화')
        
        return {
            'df_expenditure': df_expenditure,
            'df_weights': df_weights,
            'df_raw_mei_inf': df_raw_mei_inf,
            'df_rel_value': df_rel_value
        }

# 2. MEI Calculation (copied and adapted from 파이썬용_sgr_2027.py)
class MeiCalculator:
    def __init__(self, data):
        self.df_weights = data['df_weights']
        self.df_raw_mei_inf = data['df_raw_mei_inf']

    def _calc_raw_inf_rate(self, df_inf, year):
        """year의 물가 증가율 (year / year-1)"""
        try:
            current = df_inf.loc[year]
            prev = df_inf.loc[year - 1]
            return current / prev
        except KeyError:
            return pd.Series(np.nan, index=df_inf.columns)

    def _calc_labor_rate(self, df_inf, year):
        """인건비 지수 (year / year-3)^(1/3)"""
        try:
            current = df_inf.loc[year]
            prev_3 = df_inf.loc[year - 3]
            I_types = [col for col in df_inf.columns if '인건비' in col]
            return (current[I_types] / prev_3[I_types]) ** (1/3)
        except KeyError:
            return pd.Series(np.nan, index=[col for col in df_inf.columns if '인건비' in col])

    def calc_mei_16(self, year):
        labor_rates = self._calc_labor_rate(self.df_raw_mei_inf, year)
        raw_rates = self._calc_raw_inf_rate(self.df_raw_mei_inf, year)
        
        if labor_rates.isnull().all() or raw_rates.isnull().all():
            return None

        mei_results = {}
        I_types = labor_rates.index.tolist()
        M_types = [col for col in raw_rates.index if '관리비' in col]
        Z_types = [col for col in raw_rates.index if '재료비' in col]
        
        for i_t in I_types:
            inf_i = labor_rates[i_t]
            for m_t in M_types:
                inf_m = raw_rates[m_t]
                for z_t in Z_types:
                    inf_z = raw_rates[z_t]
                    
                    i_num = i_t.split('_')[-1]
                    m_num = m_t.split('_')[-1]
                    z_num = z_t.split('_')[-1]
                    scenario_name = f"I{i_num}M{m_num}Z{z_num}"
                    
                    # MEI = W_I*I + W_M*M + W_Z*Z
                    mei_idx = (
                        self.df_weights['인건비'] * inf_i +
                        self.df_weights['관리비'] * inf_m +
                        self.df_weights['재료비'] * inf_z
                    )
                    mei_results[scenario_name] = mei_idx

        df_scenarios = pd.DataFrame(mei_results) # Index: 종별, Columns: Scenarios
        
        # Stats
        df_stats = pd.DataFrame({
            '평균': df_scenarios.mean(axis=1),
            '최대': df_scenarios.max(axis=1),
            '최소': df_scenarios.min(axis=1),
            '중위수': df_scenarios.median(axis=1)
        })
        
        return pd.concat([df_scenarios, df_stats], axis=1)

# 3. Model Logic
def run_mei_growth_model(target_years):
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    data = processor.load_all_data()
    mei_calc = MeiCalculator(data)
    
    # 10 categories in specific order
    CATEGORIES_10 = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    # 5 types in specific order
    TYPES_5 = ['병원', '의원', '치과', '한방', '약국']
    
    all_results_10 = {} # target_year -> DataFrame(Scenarios x 종별)
    all_results_5 = {}  # target_year -> DataFrame(Scenarios x 유형별)
    
    for ty in target_years:
        data_year = ty - 2
        df_mei_16 = mei_calc.calc_mei_16(data_year) # Index: 종별, Columns: 16 scenarios
        
        if df_mei_16 is None:
            # print(f"Skipping {ty} due to missing data for {data_year}")
            continue
            
        try:
            rv_idx = data['df_rel_value'].loc[data_year]
            # Clean rv_idx to only include valid categories
            rv_idx = rv_idx.reindex(df_mei_16.index)
        except KeyError:
            rv_idx = pd.Series(1.0, index=df_mei_16.index)
            
        # CF Adjustment Rate = (MEI - 1) - (RV - 1) + 1 (to keep it as index)
        # Simplified: CF_index = MEI - RV + 1
        df_cf_10_all = df_mei_16.subtract(rv_idx, axis=0) + 1
        
        # Filter and order 10 categories
        df_cf_10 = df_cf_10_all.reindex(CATEGORIES_10)
        all_results_10[ty] = df_cf_10
        
        # Calculate 5 types (Weighted Average)
        exp_year = data_year
        try:
            exp_weights = data['df_expenditure'].loc[exp_year]
        except KeyError:
             continue
        
        type_results = {}
        for group in TYPES_5:
            members = processor.GROUP_MAPPING[group]
            valid_members = [m for m in members if m in df_cf_10_all.index and m in exp_weights.index]
            if not valid_members: continue
            
            group_exp = exp_weights.loc[valid_members]
            total_exp = group_exp.sum()
            
            if total_exp == 0:
                type_results[group] = pd.Series(np.nan, index=df_cf_10_all.columns)
            else:
                weights = group_exp / total_exp
                type_results[group] = df_cf_10_all.loc[valid_members].mul(weights, axis=0).sum(axis=0)
        
        df_cf_5 = pd.DataFrame(type_results).T
        all_results_5[ty] = df_cf_5.reindex(TYPES_5)

    return all_results_10, all_results_5

# 4. Main execution
if __name__ == "__main__":
    target_years = list(range(2020, 2028))
    res10, res5 = run_mei_growth_model(target_years)
    
    # Save to Excel
    with pd.ExcelWriter('MEI_증가율모형_결과.xlsx') as writer:
        summary_10 = []
        for ty, df in sorted(res10.items()):
            df_pct = (df - 1) * 100
            df_pct['연도'] = ty
            summary_10.append(df_pct.reset_index().rename(columns={'index': '종별'}))
        
        if summary_10:
            df_total_10 = pd.concat(summary_10, ignore_index=True)
            cols = ['연도', '종별'] + [c for c in df_total_10.columns if c not in ['연도', '종별']]
            df_total_10[cols].to_excel(writer, sheet_name='10개_종별_조정률', index=False)
        
        summary_5 = []
        for ty, df in sorted(res5.items()):
            df_pct = (df - 1) * 100
            df_pct['연도'] = ty
            summary_5.append(df_pct.reset_index().rename(columns={'index': '유형'}))
            
        if summary_5:
            df_total_5 = pd.concat(summary_5, ignore_index=True)
            cols5 = ['연도', '유형'] + [c for c in df_total_5.columns if c not in ['연도', '유형']]
            df_total_5[cols5].to_excel(writer, sheet_name='5개_유형별_조정률', index=False)

    print("✅ MEI 증가율 모형 계산 완료. 'MEI_증가율모형_결과.xlsx' 파일로 저장되었습니다.")
    
    # Print summary for 2020 to 2027 (Average Scenario)
    print("\n[연도별 평균 시나리오 조정률 추이 (%)]")
    
    type_summary = {}
    for ty, df in sorted(res5.items()):
        type_summary[ty] = ((df['평균'] - 1) * 100).round(2)
        
    df_type_trend = pd.DataFrame(type_summary).T
    print("\n--- 5개 유형별 (평균) ---")
    print(df_type_trend)
    
    cat_summary = {}
    for ty, df in sorted(res10.items()):
        cat_summary[ty] = ((df['평균'] - 1) * 100).round(2)
        
    df_cat_trend = pd.DataFrame(cat_summary).T
    print("\n--- 10개 종별 (평균) ---")
    print(df_cat_trend)

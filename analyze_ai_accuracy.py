
import pandas as pd
import numpy as np
from ai_optimizer import BudgetFunctionSimulator

def analyze_ai_accuracy():
    print("=== AI 예산 예측 공식 검증 데이터 분석 (2021-2025) ===")
    
    # 1. 시뮬레이터 초기화
    sim = BudgetFunctionSimulator(data_file="SGR_data.xlsx")
    
    # 2. 최적 파라미터 찾기
    best_params, _ = sim.find_optimal_parameters()
    k, j = int(best_params['k']), int(best_params['j'])
    print(f"최적 파라미터: k={k}, j={j}\n")
    
    years = [2021, 2022, 2023, 2024, 2025]
    records = []
    
    for y in years:
        if y not in sim.contract.index: continue
        
        # 실제값
        actual = sim.contract.loc[y, '추가소요재정_전체']
        
        # 예측 및 중간값 추출을 위한 로직 재현
        t2 = y - 2
        t1 = y - 1
        
        exp_t2 = sim.group_exp.loc[t2, '전체'] if t2 in sim.group_exp.index else 0
        cf_t2 = sim.group_cf.loc[t2, '전체'] if t2 in sim.group_cf.index else 83.5
        vol_t2 = exp_t2 / cf_t2 if cf_t2 > 0 else 0
        
        # RVU Index (Volume Growth)
        prev_year = t2 - k
        exp_prev = sim.group_exp.loc[prev_year, '전체'] if prev_year in sim.group_exp.index else 0
        cf_prev = sim.group_cf.loc[prev_year, '전체'] if prev_year in sim.group_cf.index else 83.5
        
        rvu_idx = 1.0
        if exp_prev > 0 and cf_prev > 0:
            vol_prev = exp_prev / cf_prev
            cagr = (vol_t2 / vol_prev) ** (1/k) - 1
            rvu_idx = (1 + cagr) ** j
            
        cf_t1 = sim.group_cf.loc[t1, '전체'] if t1 in sim.group_cf.index else 85.0
        rate = sim.group_rate.loc[y, '전체'] / 100 if y in sim.group_rate.index else 0.02
        benefit_rate = 0.77
        if '급여율' in sim.finance.columns and y in sim.finance.index:
            benefit_rate = sim.finance.loc[y, '급여율'] / 100
            
        # 최종 예측치
        pred = vol_t2 * rvu_idx * cf_t1 * rate * benefit_rate
        
        error_pct = abs(pred - actual) / actual * 100 if actual > 0 else 0
        
        records.append({
            '연도': y,
            '실제_재정(억)': round(actual, 1),
            '예측_재정(억)': round(pred, 1),
            '오차율(%)': f"{error_pct:.2f}%",
            'Vol(t-2)': round(vol_t2, 1),
            'RVU_Idx': round(rvu_idx, 3),
            'CF(t-1)': round(cf_t1, 1),
            '인상률(%)': f"{rate*100:.2f}%",
            '급여율(%)': f"{benefit_rate*100:.1f}%"
        })
        
    df = pd.DataFrame(records)
    print(df.to_string(index=False))
    
    # 평균 오차율
    mean_err = df['오차율(%)'].str.replace('%', '').astype(float).mean()
    print(f"\n평균 검증 오차율: {mean_err:.2f}%")

if __name__ == "__main__":
    analyze_ai_accuracy()

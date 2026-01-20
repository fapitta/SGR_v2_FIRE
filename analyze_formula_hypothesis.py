"""
데이터 및 공식 정밀 분석 스크립트
1. RVS 시트 데이터 확인 (0% 증가율 원인 파악)
2. '총 증가분' 가설 테스트
"""

import pandas as pd
import numpy as np

contract = pd.read_excel('SGR_data.xlsx', sheet_name='contract', index_col=0)
expenditure = pd.read_excel('SGR_data.xlsx', sheet_name='expenditure_real', index_col=0)
cf = pd.read_excel('SGR_data.xlsx', sheet_name='cf_t', index_col=0)
rvs = pd.read_excel('SGR_data.xlsx', sheet_name='rvs', index_col=0)

hospital_types = ['병원(계)', '의원', '치과(계)', '한방(계)', '약국']
rvs_cols = [col for col in rvs.columns if col in hospital_types]

print('='*70)
print('1. RVS 시트 데이터 확인')
print('='*70)
print(rvs[rvs_cols].head())
print('...')
print(rvs[rvs_cols].tail())

print('\n년도별 RVS 평균값 및 증가율:')
rvs_vals = rvs[rvs_cols].mean(axis=1)
for year in range(2015, 2026):
    if year in rvs_vals.index:
        val = rvs_vals.loc[year]
        growth = 0
        if (year-1) in rvs_vals.index:
            prev = rvs_vals.loc[year-1]
            growth = (val - prev) / prev if prev > 0 else 0
        print(f'{year}: {val:.4f} (증가율: {growth*100:+.2f}%)')

print('\n' + '='*70)
print('2. "총 증가분" 가설 테스트')
print('공식: 예산 = 행위진료비(t-2) * [ (1+RVU_avg)^j * (1+CF(t-1)) * (1+CF(t)) - 1 ] * 급여율')
print('='*70)

# RVU 증가율이 0이면 임의값(3%?)을 넣어 테스트하거나, 
# 행위진료비 역산으로 추정된 RVU 증가율 사용
estimated_rvu_growth = 0.03 # 3% 가정

for j_test in [1, 2]:
    print(f'\n[Num Years j = {j_test}]')
    for year in [2021, 2022, 2023, 2024, 2025]:
        exp_cols = [col for col in expenditure.columns if col in hospital_types]
        exp_base = expenditure.loc[year-2, exp_cols].sum()
        
        # RVU Factor (3% 가정)
        rvu_factor = (1 + estimated_rvu_growth) ** j_test
        
        # CF Factors
        cf_rate_prev = contract.loc[year-1, '인상율_전체'] / 100 if (year-1) in contract.index else 0.02
        cf_rate_curr = contract.loc[year, '인상율_전체'] / 100
        
        cf_factor_prev = 1 + cf_rate_prev
        cf_factor_curr = 1 + cf_rate_curr
        
        # Benefit
        ben = 0.63
        
        # Formula: Total Increase
        total_growth_factor = rvu_factor * cf_factor_prev * cf_factor_curr
        increase_rate = total_growth_factor - 1
        
        pred = exp_base * increase_rate * ben
        
        act = contract.loc[year, '추가소요재정_전체']
        err = ((pred - act) / act) * 100
        
        print(f'{year}년: 예측 {pred:,.0f} vs 실제 {act:,.0f} (오차 {err:+.1f}%)')
        print(f'   Factors: RVU={rvu_factor:.3f}, CF(t-1)={cf_factor_prev:.3f}, CF(t)={cf_factor_curr:.3f}')
        print(f'   Increase Rate: {increase_rate*100:.2f}%')

print('\n' + '='*70)
print('3. 역산: 필요한 RVU 증가율 찾기')
print('='*70)
# 실제 예산이 나오기 위해 필요한 RVU 증가율 역산
# Act = Exp * [ (1+x)^j * CFs - 1 ] * Ben
# Act / (Exp * Ben) = Increase_Rate
# Increase_Rate + 1 = Total_Factor
# (1+x)^j = Total_Factor / CFs
# 1+x = (Total_Factor / CFs)^(1/j)

required_rvu_growths = []
for year in [2021, 2022, 2023, 2024, 2025]:
    exp_base = expenditure.loc[year-2, exp_cols].sum()
    act = contract.loc[year, '추가소요재정_전체']
    ben = 0.63
    
    cf_rate_prev = contract.loc[year-1, '인상율_전체'] / 100 if (year-1) in contract.index else 0.02
    cf_rate_curr = contract.loc[year, '인상율_전체'] / 100
    cf_combined = (1 + cf_rate_prev) * (1 + cf_rate_curr)
    
    target_increase = act / (exp_base * ben)
    target_total = target_increase + 1
    
    required_rvu_factor = target_total / cf_combined
    
    # j=1 가정
    required_rvu = required_rvu_factor - 1
    required_rvu_growths.append(required_rvu)
    
    print(f'{year}년 필요 RVU 증가율 (j=1): {required_rvu*100:.2f}%')

print(f'\n평균 필요 RVU 증가율: {np.mean(required_rvu_growths)*100:.2f}%')

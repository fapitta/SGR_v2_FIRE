import pandas as pd
import numpy as np

contract = pd.read_excel('SGR_data.xlsx', sheet_name='contract', index_col=0)
expenditure = pd.read_excel('SGR_data.xlsx', sheet_name='expenditure_real', index_col=0)
rvs = pd.read_excel('SGR_data.xlsx', sheet_name='rvs', index_col=0)

hospital_types = ['병원(계)', '의원', '치과(계)', '한방(계)', '약국']
exp_cols = [col for col in expenditure.columns if col in hospital_types]
rvs_cols = [col for col in rvs.columns if col in hospital_types]

print('='*70)
print('수정된 공식 테스트 (k=4, j=1)')
print('='*70)
print('\n공식: 추가소요재정(t) = 행위진료비(t-2) × RVU지수(k,j) × (1 + 환산지수조정률(t)) × 급여율(t)')
print('='*70)

for year in [2021, 2022, 2023, 2024, 2025]:
    # 행위진료비(t-2)
    exp_base = expenditure.loc[year-2, exp_cols].sum()
    
    # RVU 지수
    rvs_vals = rvs[rvs_cols].mean(axis=1)
    gr = []
    for y in range(year-4+1, year-2+1):
        if y in rvs_vals.index and (y-1) in rvs_vals.index and rvs_vals.loc[y-1] > 0:
            gr.append((rvs_vals.loc[y] - rvs_vals.loc[y-1]) / rvs_vals.loc[y-1])
    rvu_idx = (1 + np.mean(gr)) ** 1 if gr else 1.0
    
    # 환산지수조정률(t)
    cf_adj = contract.loc[year, '인상율_전체'] / 100
    
    # 급여율
    ben = 0.63
    
    # 예측 (수정된 공식!)
    pred = exp_base * rvu_idx * (1 + cf_adj) * ben
    
    # 실제
    act = contract.loc[year, '추가소요재정_전체']
    
    # 오차
    err = ((pred - act) / act) * 100
    
    print(f'\n{year}년:')
    print(f'  행위진료비({year-2}): {exp_base:,.0f} 억원')
    print(f'  RVU지수: {rvu_idx:.4f}')
    print(f'  환산지수조정률: {cf_adj*100:.2f}%')
    print(f'  (1 + 환산지수조정률): {1+cf_adj:.4f}')
    print(f'  급여율: {ben*100:.0f}%')
    print(f'  예측: {pred:,.0f} 억원')
    print(f'  실제: {act:,.0f} 억원')
    print(f'  오차율: {err:+.2f}%')

print('\n' + '='*70)
print('다양한 k 값 테스트')
print('='*70)

for k in range(1, 6):
    errors = []
    for year in [2021, 2022, 2023, 2024, 2025]:
        exp_base = expenditure.loc[year-2, exp_cols].sum()
        rvs_vals = rvs[rvs_cols].mean(axis=1)
        gr = []
        for y in range(year-k+1, year-2+1):
            if y in rvs_vals.index and (y-1) in rvs_vals.index and rvs_vals.loc[y-1] > 0:
                gr.append((rvs_vals.loc[y] - rvs_vals.loc[y-1]) / rvs_vals.loc[y-1])
        rvu_idx = (1 + np.mean(gr)) ** 1 if gr else 1.0
        cf_adj = contract.loc[year, '인상율_전체'] / 100
        ben = 0.63
        pred = exp_base * rvu_idx * (1 + cf_adj) * ben
        act = contract.loc[year, '추가소요재정_전체']
        err = ((pred - act) / act) * 100
        errors.append(err)
    
    avg_err = np.mean(np.abs(errors))
    print(f'\nk={k}: 평균 절대 오차율 = {avg_err:.2f}%')
    print(f'  연도별: {", ".join([f"{e:+.1f}%" for e in errors])}')

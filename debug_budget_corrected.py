"""
추가소요재정 함수 디버깅 스크립트 (최종 수정본)
올바른 공식: 환산지수조정률(t) = 실제 환산지수 인상률 사용
"""

import pandas as pd
import numpy as np

# 데이터 로드
contract = pd.read_excel('SGR_data.xlsx', sheet_name='contract', index_col=0)
expenditure = pd.read_excel('SGR_data.xlsx', sheet_name='expenditure_real', index_col=0)
cf = pd.read_excel('SGR_data.xlsx', sheet_name='cf_t', index_col=0)
rvs = pd.read_excel('SGR_data.xlsx', sheet_name='rvs', index_col=0)

try:
    finance = pd.read_excel('SGR_data.xlsx', sheet_name='finance', index_col=0)
    if '급여율' in finance.columns:
        benefit_rate = finance['급여율'] / 100
    else:
        benefit_rate = pd.Series(0.63, index=finance.index)
except:
    benefit_rate = pd.Series(0.63, index=range(2008, 2028))

hospital_types = ['병원(계)', '의원', '치과(계)', '한방(계)', '약국']

print("="*70)
print("추가소요재정 함수 디버깅 (최종 수정본)")
print("="*70)
print("\n올바른 공식:")
print("추가소요재정(t) = 행위진료비(t-2) × RVU증가지수(k,j) × ")
print("                   환산지수조정률(t) × 급여율(t)")
print("\n여기서 환산지수조정률(t) = 실제 환산지수 인상률 (contract 시트의 인상율)")
print("="*70)

# 2021년 예시로 상세 계산
year = 2021
k = 4
j = 1

print(f"\n[상세 계산] {year}년, k={k}, j={j}")
print("-"*70)

# 1. 행위진료비(t-2)
exp_year = year - 2  # 2019
exp_cols = [col for col in expenditure.columns if col in hospital_types]
expenditure_base = expenditure.loc[exp_year, exp_cols].sum()
print(f"\n1. 행위진료비({exp_year}년): {expenditure_base:,.0f} 억원")

# 2. RVU 증가지수
start_year = year - k  # 2017
end_year = year - 2    # 2019

print(f"\n2. RVU 증가지수 계산:")
print(f"   참조 기간: {start_year}년 ~ {end_year}년")

rvs_cols = [col for col in rvs.columns if col in hospital_types]
rvs_values = rvs[rvs_cols].mean(axis=1)

growth_rates = []
for y in range(start_year + 1, end_year + 1):
    if y in rvs_values.index and (y-1) in rvs_values.index:
        prev_val = rvs_values.loc[y-1]
        curr_val = rvs_values.loc[y]
        if prev_val > 0:
            growth_rate = (curr_val - prev_val) / prev_val
            growth_rates.append(growth_rate)
            print(f"   {y}: {prev_val:.4f} → {curr_val:.4f}, 증가율: {growth_rate*100:+.2f}%")

avg_growth_rate = np.mean(growth_rates) if growth_rates else 0
rvu_index = (1 + avg_growth_rate) ** j
print(f"   평균 증가율: {avg_growth_rate*100:.2f}%")
print(f"   RVU 지수 (j={j}년 적용): {rvu_index:.4f}")

# 3. 환산지수조정률(t) = 실제 인상률
cf_adjustment_rate = contract.loc[year, '인상율_전체'] / 100
print(f"\n3. 환산지수조정률({year}년): {cf_adjustment_rate*100:.2f}%")
print(f"   (contract 시트의 실제 인상율 사용)")

# 4. 급여율(t)
if year in benefit_rate.index:
    ben_rate = benefit_rate.loc[year]
else:
    ben_rate = 0.63
print(f"\n4. 급여율({year}년): {ben_rate*100:.2f}%")

# 최종 계산
predicted = expenditure_base * rvu_index * (1 + cf_adjustment_rate) * ben_rate

print(f"\n{'='*70}")
print(f"최종 계산:")
print(f"{'='*70}")
print(f"예측값 = {expenditure_base:,.0f} × {rvu_index:.4f} × {1+cf_adjustment_rate:.4f} × {ben_rate:.4f}")
print(f"       = {predicted:,.0f} 억원")

# 실제값
actual = contract.loc[year, '추가소요재정_전체']
print(f"\n실제값 = {actual:,.0f} 억원")

# 오차율 계산
error_rate = ((predicted - actual) / actual) * 100
print(f"\n오차율 = (예측값 - 실제값) / 실제값 × 100")
print(f"       = ({predicted:,.0f} - {actual:,.0f}) / {actual:,.0f} × 100")
print(f"       = {error_rate:+.2f}%")

print(f"\n{'='*70}")
print("전체 연도 테스트 (k=4, j=1)")
print(f"{'='*70}")

results = []
for test_year in [2021, 2022, 2023, 2024, 2025]:
    exp_year = test_year - 2
    
    # 행위진료비
    exp_cols = [col for col in expenditure.columns if col in hospital_types]
    exp_base = expenditure.loc[exp_year, exp_cols].sum()
    
    # RVU 지수
    start_y = test_year - k
    end_y = test_year - 2
    rvs_vals = rvs[rvs_cols].mean(axis=1)
    
    gr = []
    for y in range(start_y + 1, end_y + 1):
        if y in rvs_vals.index and (y-1) in rvs_vals.index:
            pv = rvs_vals.loc[y-1]
            cv = rvs_vals.loc[y]
            if pv > 0:
                gr.append((cv - pv) / pv)
    
    avg_gr = np.mean(gr) if gr else 0
    rvu_idx = (1 + avg_gr) ** j
    
    # 환산지수조정률(t) = 실제 인상률
    cf_adj = contract.loc[test_year, '인상율_전체'] / 100
    
    # 급여율
    ben = benefit_rate.loc[test_year] if test_year in benefit_rate.index else 0.63
    
    # 예측
    pred = exp_base * rvu_idx * (1 + cf_adj) * ben
    
    # 실제
    act = contract.loc[test_year, '추가소요재정_전체']
    
    # 오차
    err = ((pred - act) / act) * 100
    
    results.append({
        'year': test_year,
        'exp_base': exp_base,
        'rvu_idx': rvu_idx,
        'cf_adj': cf_adj,
        'benefit': ben,
        'predicted': pred,
        'actual': act,
        'error': err
    })
    
    print(f"\n{test_year}년:")
    print(f"  행위진료비({exp_year}): {exp_base:,.0f} 억원")
    print(f"  RVU지수: {rvu_idx:.4f}")
    print(f"  환산지수조정률: {cf_adj*100:.2f}%")
    print(f"  급여율: {ben*100:.2f}%")
    print(f"  예측: {pred:,.0f} 억원")
    print(f"  실제: {act:,.0f} 억원")
    print(f"  오차율: {err:+.2f}%")

print(f"\n{'='*70}")
print("다양한 k 값 테스트 (j=1 고정)")
print(f"{'='*70}")

best_k = None
best_error = float('inf')

for k_test in range(1, 6):
    errors = []
    for test_year in [2021, 2022, 2023, 2024, 2025]:
        exp_year = test_year - 2
        exp_cols = [col for col in expenditure.columns if col in hospital_types]
        exp_base = expenditure.loc[exp_year, exp_cols].sum()
        
        start_y = test_year - k_test
        end_y = test_year - 2
        rvs_vals = rvs[rvs_cols].mean(axis=1)
        
        gr = []
        for y in range(start_y + 1, end_y + 1):
            if y in rvs_vals.index and (y-1) in rvs_vals.index:
                pv = rvs_vals.loc[y-1]
                cv = rvs_vals.loc[y]
                if pv > 0:
                    gr.append((cv - pv) / pv)
        
        avg_gr = np.mean(gr) if gr else 0
        rvu_idx = (1 + avg_gr) ** 1
        
        # 환산지수조정률 = 실제 인상률
        cf_adj = contract.loc[test_year, '인상율_전체'] / 100
        
        ben = benefit_rate.loc[test_year] if test_year in benefit_rate.index else 0.63
        
        pred = exp_base * rvu_idx * (1 + cf_adj) * ben
        act = contract.loc[test_year, '추가소요재정_전체']
        err = ((pred - act) / act) * 100
        errors.append(err)
    
    avg_err = np.mean(np.abs(errors))
    
    if avg_err < best_error:
        best_error = avg_err
        best_k = k_test
    
    marker = " ← 최적!" if k_test == best_k else ""
    print(f"\nk={k_test}: 평균 절대 오차율 = {avg_err:.2f}%{marker}")
    print(f"  연도별: {', '.join([f'{e:+.1f}%' for e in errors])}")

print(f"\n{'='*70}")
print(f"최적 파라미터: k={best_k}, j=1")
print(f"평균 절대 오차율: {best_error:.2f}%")
print(f"{'='*70}")

# 사용자 수동 계산 결과와 비교
print(f"\n{'='*70}")
print("사용자 수동 계산 결과와 비교")
print(f"{'='*70}")
print("\n사용자 결과 (k=4, j=1):")
print("  2021년: -4.6%")
print("  2022년: -2.3%")
print("  2023년:  0.0%")
print("  2024년: -3.0%")
print("  2025년: +1.8%")

print("\n현재 계산 결과 (k=4, j=1):")
for r in results:
    print(f"  {r['year']}년: {r['error']:+.1f}%")

print(f"\n{'='*70}")
print("공식 요약")
print(f"{'='*70}")
print("추가소요재정(t) = 행위진료비(t-2) × RVU증가지수(k,j) × ")
print("                   (1 + 환산지수조정률(t)) × 급여율(t)")
print("\n여기서:")
print("- 환산지수조정률(t) = contract 시트의 '인상율_전체' (실제 수가 인상률)")
print("- RVU증가지수(k,j) = (1 + avg_RVU_growth_rate)^j")
print("- avg_RVU_growth_rate = (t-k)년 ~ (t-2)년 기간의 평균 RVU 증가율")

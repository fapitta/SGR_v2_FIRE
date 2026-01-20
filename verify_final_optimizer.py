
from ai_optimizer import BudgetFunctionSimulator
import pandas as pd

simulator = BudgetFunctionSimulator('SGR_data.xlsx')

print("="*60)
print("AI Optimizer Verification (k=4, j=1)")
print("Target: Match user's manual calculation (-4.6% to +1.8%)")
print("="*60)

years = [2021, 2022, 2023, 2024, 2025]
k, j = 4, 1

for y in years:
    pred = simulator.predict_budget(y, k, j)
    # 실제 추가소요재정_전체
    actual = simulator.contract.loc[y, '추가소요재정_전체']
    err = ((pred - actual) / actual) * 100
    
    print(f"{y}년: 예측 {pred:,.0f} vs 실제 {actual:,.0f} (오차 {err:+.1f}%)")

# 전체 파라미터 시뮬레이션 결과 확인
best, results = simulator.find_optimal_parameters(k_range=(1,5), j_range=(1,3))
print("\n" + "="*60)
print(f"Optimal Parameters Found: k={best['k']}, j={best['j']}, Error={best['abs_mean_error']:.2f}%")
print("="*60)
print(results.sort_values('abs_mean_error').head(5))

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator
import pandas as pd

def debug_sgr_s1():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    engine_data = processor.raw_data
    hospital_types = ['상급종합', '병원']  # Focus on these for brevity
    
    sgr_calc = SgrCalculator(engine_data, hospital_types)
    
    print("\n=== 2025년 SGR(S1) UAF(PAF) 상세 검증 (상급종합, 병원) ===")
    
    target_year = 2025
    ae_actual = sgr_calc.data['df_expenditure']
    
    # 1. 단기 균형 (Short-term)
    # y_recent = 2023
    y_recent = target_year - 2
    
    c_recent = sgr_calc._calc_sgr_components(y_recent)
    idx_recent = sgr_calc.calc_sgr_index(c_recent, model='S1')
    
    ae_prev = sgr_calc._safe_get(ae_actual, y_recent-1) # 2022 Actual
    ae_curr = sgr_calc._safe_get(ae_actual, y_recent)   # 2023 Actual
    
    tge_recent = ae_prev * idx_recent
    gap_short = (tge_recent - ae_curr) / ae_curr
    
    print(f"\n[1. 단기 균형 (Short-term)] Target Year: {target_year} -> Calc Year: {y_recent}")
    for h in hospital_types:
        print(f">> {h}:")
        print(f"   Actual({y_recent-1}): {ae_prev[h]:,.0f}")
        print(f"   SGR Index({y_recent}): {idx_recent[h]:.6f}")
        print(f"   Target({y_recent}): {tge_recent[h]:,.0f}")
        print(f"   Actual({y_recent}): {ae_curr[h]:,.0f}")
        print(f"   Gap Short (Raw): {gap_short[h]:.6f}")

    # 2. 누적 균형 (Accumulated)
    # y: 2014 ~ 2023
    y_start, y_end = target_year-11, target_year-2
    print(f"\n[2. 누적 균형 (Accumulated)] Years: {y_start} ~ {y_end}")
    
    sum_tge = pd.Series(0.0, index=sgr_calc.hospital_types)
    sum_ae = pd.Series(0.0, index=sgr_calc.hospital_types)
    
    debug_accum_table = []
    
    for y in range(y_start, y_end + 1):
        c = sgr_calc._calc_sgr_components(y)
        idx = sgr_calc.calc_sgr_index(c, model='S1')
        
        ae_y_prev = sgr_calc._safe_get(ae_actual, y-1)
        ae_y = sgr_calc._safe_get(ae_actual, y)
        
        tge_y = ae_y_prev * idx
        
        sum_tge += tge_y
        sum_ae += ae_y
        
        if y >= 2020: # Print recent years for check
             for h in hospital_types:
                 debug_accum_table.append({
                     'Year': y, 'Type': h,
                     'Ae_Prev': ae_y_prev[h], 'SGR': idx[h], 'Target': tge_y[h], 'Actual': ae_y[h]
                 })

    # Debug Accum Table (Last few years)
    print("\n   --- 누적 계산 상세 (2020~2023) ---")
    for r in debug_accum_table:
        print(f"   {r['Year']} {r['Type']}: T({r['Target']:,.0f}) = A_prev({r['Ae_Prev']:,.0f}) * SGR({r['SGR']:.4f}) | Act({r['Actual']:,.0f})")

    # Denom Logic
    c_prev = sgr_calc._calc_sgr_components(target_year-1) # 2024
    idx_prev = sgr_calc.calc_sgr_index(c_prev, model='S1') # SGR(2024)
    denom = sgr_calc._safe_get(ae_actual, target_year-2) * idx_prev # AE(2023) * SGR(2024)
    
    gap_accum = (sum_tge - sum_ae) / denom
    
    print(f"\n[Term Totals]")
    for h in hospital_types:
        print(f">> {h}:")
        print(f"   Sum Target: {sum_tge[h]:,.0f}")
        print(f"   Sum Actual: {sum_ae[h]:,.0f}")
        print(f"   Diff: {sum_tge[h] - sum_ae[h]:,.0f}")
        print(f"   Denom (AE_2023 * SGR_2024): {denom[h]:,.0f}")
        print(f"   Gap Accum (Raw): {gap_accum[h]:.6f}")

    # 3. Final PAF
    # paf = gap_short * 0.75 + gap_accum * 0.33
    paf = gap_short * 0.75 + gap_accum * 0.33
    
    print(f"\n[3. 최종 PAF (UAF)] Formula: Gap_Short * 0.75 + Gap_Accum * 0.33")
    for h in hospital_types:
        print(f">> {h}:")
        print(f"   {gap_short[h]:.6f} * 0.75 + {gap_accum[h]:.6f} * 0.33 = {paf[h]:.6f} ({paf[h]*100:.2f}%)")

if __name__ == "__main__":
    debug_sgr_s1()

from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine
import pandas as pd

def debug_full_status():
    print("=== 1. Initialize System ===")
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    engine = CalculationEngine(processor.raw_data)
    
    print("\n=== 2. Check MEI Scenarios (2025) ===")
    mei_2025 = engine.mei_calc.calc_mei_index_by_year(2025)
    if mei_2025 is not None:
        print(f"MEI DataFrame Shape: {mei_2025.shape}")
        print("Columns (Scenarios):", mei_2025.columns.tolist())
        print("Rows (Hospital Types):", mei_2025.index.tolist())
        print("Sample Data (First row):")
        print(mei_2025.iloc[0])
    else:
        print("❌ MEI Calculation returned None!")

    print("\n=== 3. Check SGR UAF 2025 Calculation (S1) ===")
    target_year = 2025
    sgr_calc = engine.sgr_calc
    
    # Manually reproduce calc_paf_s1 logic to show details
    ae_actual = sgr_calc.data['df_expenditure']
    
    # 3-1. Short Term (2023)
    y_recent = target_year - 2 # 2023
    c_recent = sgr_calc._calc_sgr_components(y_recent)
    idx_recent = sgr_calc.calc_sgr_index(c_recent, model='S1')
    ae_prev_short = sgr_calc._safe_get(ae_actual, y_recent-1) # 2022
    tge_recent = ae_prev_short * idx_recent
    ae_curr_short = sgr_calc._safe_get(ae_actual, y_recent) # 2023
    
    gap_short_raw = (tge_recent - ae_curr_short) / ae_curr_short

    # 3-2. Accumulated (2014-2023)
    y_start, y_end = target_year-11, target_year-2
    sum_tge = 0
    sum_ae = 0
    
    print(f"\n[Accumulation Period Check]")
    print(f"Looping from {y_start} to {y_end}...")
    
    debug_accum_log = []
    
    for y in range(y_start, y_end + 1):
        c = sgr_calc._calc_sgr_components(y)
        idx = sgr_calc.calc_sgr_index(c, model='S1')
        
        ae_prev_y = sgr_calc._safe_get(ae_actual, y-1)
        ae_curr_y = sgr_calc._safe_get(ae_actual, y)
        
        tge_y = ae_prev_y * idx
        
        sum_tge += tge_y
        sum_ae += ae_curr_y
        
        # Log first and last few years to verify
        if y <= 2015 or y >= 2022:
             debug_accum_log.append(f"  {y}: Actual({y-1})={ae_prev_y['상급종합']:,.0f} * SGR={idx['상급종합']:.4f} -> Target={tge_y['상급종합']:,.0f} | Actual({y})={ae_curr_y['상급종합']:,.0f}")
    
    for l in debug_accum_log:
        print(l)

    # 3-3. Denominator (2023 Actual * 2024 SGR)
    c_prev = sgr_calc._calc_sgr_components(target_year-1) # 2024
    idx_prev = sgr_calc.calc_sgr_index(c_prev, model='S1')
    denom = sgr_calc._safe_get(ae_actual, target_year-2) * idx_prev
    
    gap_accum_raw = (sum_tge - sum_ae) / denom # This is the raw gap ratio
    
    # 3-4. Final UAF Formula
    # Formula: Gap_Short * 0.75 + Gap_Accum * 0.33
    uaf_final = gap_short_raw * 0.75 + gap_accum_raw * 0.33

    print(f"\n[Checking Values for '상급종합']")
    h = '상급종합'
    print(f"1. Short Term (2023 Gap)")
    print(f"   Target(2023): {tge_recent[h]:,.0f}")
    print(f"   Actual(2023): {ae_curr_short[h]:,.0f}")
    print(f"   Gap Short = ({tge_recent[h]:,.0f} - {ae_curr_short[h]:,.0f}) / {ae_curr_short[h]:,.0f} = {gap_short_raw[h]:.6f}")
    
    print(f"\n2. Accumulated (2014-2023 Gap)")
    print(f"   Sum Target: {sum_tge[h]:,.0f}")
    print(f"   Sum Actual: {sum_ae[h]:,.0f}")
    print(f"   Diff: {sum_tge[h] - sum_ae[h]:,.0f}")
    print(f"   Denominator (AE_2023 * SGR_2024): {denom[h]:,.0f}")
    print(f"   Gap Accum = {sum_tge[h] - sum_ae[h]:,.0f} / {denom[h]:,.0f} = {gap_accum_raw[h]:.6f}")

    print(f"\n3. Final UAF Calculation")
    print(f"   UAF_2025 = ({gap_short_raw[h]:.6f} * 0.75) + ({gap_accum_raw[h]:.6f} * 0.33)")
    print(f"            = {gap_short_raw[h]*0.75:.6f} + {gap_accum_raw[h]*0.33:.6f}")
    print(f"            = {uaf_final[h]:.6f} ({uaf_final[h]*100:.2f}%)")

if __name__ == "__main__":
    debug_full_status()

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator
import pandas as pd

def audit_accumulation_steps(target_type='한의원'):
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    # Mocking CalculationEngine structure
    hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    group_mapping = {
        '병원(계)': ['상급종합', '종합병원', '병원', '요양병원'], '의원(계)': ['의원'],
        '치과(계)': ['치과병원', '치과의원'], '한방(계)': ['한방병원', '한의원'], '약국(계)': ['약국']
    }
    sgr_calc = SgrCalculator(processor.raw_data, hospital_types, group_mapping)
    ae = processor.raw_data['df_expenditure']
    
    print(f"=== [Audit] 10-Year Accumulation Detail for {target_type} (Target: 2025) ===")
    print(f"{'Year':<6} | {'AE_prev':<10} | {'SGR_Idx':<10} | {'Target_E':<10} | {'Actual_E':<10} | {'Gap'}")
    print("-" * 75)
    
    sum_tge = 0
    sum_ae = 0
    
    # 2014 to 2023
    for y in range(2014, 2024):
        comp = sgr_calc._calc_sgr_components(y)
        idx = sgr_calc.calc_sgr_index(comp, 'S1')[target_type]
        a_prev = ae.loc[y-1, target_type]
        a_curr = ae.loc[y, target_type]
        tge = a_prev * idx
        
        sum_tge += tge
        sum_ae += a_curr
        
        print(f"{y:<6} | {a_prev:10.2f} | {idx:10.4f} | {tge:10.2f} | {a_curr:10.2f} | {tge-a_curr:10.2f}")
    
    print("-" * 75)
    print(f"Total  | {'-':<10} | {'-':<10} | {sum_tge:10.2f} | {sum_ae:10.2f} | {sum_tge-sum_ae:10.2f}")
    
    c_24 = sgr_calc._calc_sgr_components(2024)
    idx_24 = sgr_calc.calc_sgr_index(c_24, 'S1')[target_type]
    ae_23 = ae.loc[2023, target_type]
    denom = ae_23 * (1 + idx_24)
    gap_accum = (sum_tge - sum_ae) / denom
    
    # Short term Gap (2023)
    # TGE_2023 was already calc in loop
    comp_23 = sgr_calc._calc_sgr_components(2023)
    idx_23 = sgr_calc.calc_sgr_index(comp_23, 'S1')[target_type]
    ae_22 = ae.loc[2022, target_type]
    tge_23 = ae_22 * idx_23
    gap_short = (tge_23 - ae_23) / ae_23
    
    uaf_s1 = gap_short * 0.75 + gap_accum * 0.33
    
    print(f"\n[Components of UAF_2025]")
    print(f"1. Gap_Short (2023): ({tge_23:.2f} - {ae_23:.2f}) / {ae_23:.2f} = {gap_short:.6f}")
    print(f"2. Denominator: {ae_23:.2f} * (1 + {idx_24:.4f}) = {denom:.2f}")
    print(f"3. Gap_Accum: ({sum_tge:.2f} - {sum_ae:.2f}) / {denom:.2f} = {gap_accum:.6f}")
    print(f"4. S1 UAF: ({gap_short:.6f} * 0.75) + ({gap_accum:.6f} * 0.33) = {uaf_s1:.6f} ({uaf_s1*100:.3f}%)")

    # Inspect Factors for 2024 to see why oriental might differ
    print(f"\n[2024 Factors for {target_type}]")
    comp_24 = sgr_calc._calc_sgr_components(2024)
    print(f"g_s1: {comp_24['g_s1']:.5f}")
    print(f"p_s1: {comp_24['p_s1']:.5f}")
    print(f"l: {comp_24['l'][target_type]:.5f}")
    print(f"r: {comp_24['r'][target_type]:.5f}")

if __name__ == "__main__":
    audit_accumulation_steps('한의원')
    print("\n" + "="*80 + "\n")
    audit_accumulation_steps('종합병원')

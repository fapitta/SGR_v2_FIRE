from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine
import pandas as pd

def debug_dental_oriental_2025():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    engine = CalculationEngine(processor.raw_data)
    target_year = 2025
    
    target_types = ['치과병원', '치과의원', '한방병원', '한의원']
    target_groups = ['치과(계)', '한방(계)']
    
    # 1. MEI 2025 (Average)
    df_mei = engine.mei_calc.calc_mei_index_by_year(target_year)
    mei_avg = df_mei['평균']
    
    # 2. UAF S1 and S2
    uaf_s1 = engine.sgr_calc.calc_paf_s1(target_year)
    uaf_s2 = engine.sgr_calc.calc_paf_s2(target_year)
    
    # 3. Components for UAF S1 (To debug)
    ae = processor.raw_data['df_expenditure']
    
    print(f"=== [Debug] 2025 SGR(S1) Calculation Breakdown ===")
    print(f"Formula: UAF = (Gap_Short * 0.75 + Gap_Accum * 0.33)")
    print(f"Gap_Accum Denom: AE_2023 * (1 + SGR_Index_2024)")
    print("-" * 60)
    
    for t in target_types:
        # Short Term Detail
        y_short = target_year - 2 # 2023
        comp_23 = engine.sgr_calc._calc_sgr_components(y_short)
        idx_23 = engine.sgr_calc.calc_sgr_index(comp_23, 'S1')
        ae_22 = ae.loc[2022, t]
        ae_23 = ae.loc[2023, t]
        tge_23 = ae_22 * idx_23[t]
        gap_short = (tge_23 - ae_23) / ae_23
        
        # Accum Detail
        sum_tge = 0
        sum_ae = 0
        for y in range(2014, 2024):
            c_y = engine.sgr_calc._calc_sgr_components(y)
            idx_y = engine.sgr_calc.calc_sgr_index(c_y, 'S1')
            ae_prev = ae.loc[y-1, t]
            ae_curr = ae.loc[y, t]
            sum_tge += ae_prev * idx_y[t]
            sum_ae += ae_curr
            
        c_24 = engine.sgr_calc._calc_sgr_components(2024)
        idx_24 = engine.sgr_calc.calc_sgr_index(c_24, 'S1')
        denom = ae_23 * (1 + idx_24[t])
        gap_accum = (sum_tge - sum_ae) / denom
        
        uaf_s1_calc = gap_short * 0.75 + gap_accum * 0.33
        
        print(f"[{t}]")
        print(f"  - MEI 2025(Avg): {mei_avg[t]:.4f}")
        print(f"  - Gap Short(2023): (Target:{tge_23:,.2f} - Actual:{ae_23:,.2f}) / Actual = {gap_short:.6f}")
        print(f"  - Gap Accum(2014-23): (SumT:{sum_tge:,.2f} - SumA:{sum_ae:,.2f}) / Denom:{denom:,.2f} = {gap_accum:.6f}")
        print(f"  - UAF_S1: ({gap_short:.4f}*0.75) + ({gap_accum:.4f}*0.33) = {uaf_s1_calc:.6f} ({uaf_s1_calc*100:.2f}%)")
        
        # Final CF S1
        cf_s1_idx = mei_avg[t] * (1 + uaf_s1_calc)
        cf_s1_rate = (cf_s1_idx - 1) * 100
        print(f"  - Final CF(S1): {mei_avg[t]:.4f} * (1 + {uaf_s1_calc:.4f}) = {cf_s1_idx:.4f} -> {cf_s1_rate:.2f}%")
        print("-" * 30)

    print("\n=== [Group Averages (치과, 한방)] ===")
    history, details, bulk = engine.run_full_analysis(2025)
    
    for g in target_groups:
        res_s1 = bulk['scenario_adjustments'][2025]['평균']['S1'][g]
        res_s2 = bulk['scenario_adjustments'][2025]['평균']['S2'][g]
        print(f"[{g}] Final Adjustment (Scenario: 평균)")
        print(f"  - S1: {res_s1}%")
        print(f"  - S2: {res_s2}%")

if __name__ == "__main__":
    debug_dental_oriental_2025()

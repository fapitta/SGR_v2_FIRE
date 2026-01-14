import pandas as pd
import numpy as np

def debug_uaf_2025_s1_fixed():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator
    
    processor = DataProcessor(EXCEL_FILE_PATH)
    sgr_calc = SgrCalculator(processor.data, processor.HOSPITAL_TYPES)
    df_ae = processor.data['df_expenditure']
    
    T = 2025
    y_recent = T - 2 # 2023
    y_next = T - 1   # 2024
    
    # 1. 단기 격차 반영 (2023년)
    comp_2023 = sgr_calc._calc_sgr_components(y_recent)
    sgr_idx_2023 = sgr_calc.calc_sgr_index(comp_2023, model='S1')['상급종합']
    ae_2022 = df_ae.loc[2022, '상급종합']
    tge_2023 = ae_2022 * sgr_idx_2023
    ae_2023 = df_ae.loc[y_recent, '상급종합']
    gap_short = (tge_2023 - ae_2023) / ae_2023
    
    # 2. 누적 격차 반영 (2014 ~ 2023)
    sum_tge = 0
    sum_ae = 0
    for y in range(T - 11, y_recent + 1):
        comp = sgr_calc._calc_sgr_components(y)
        idx = sgr_calc.calc_sgr_index(comp, model='S1')['상급종합']
        ae_prev = df_ae.loc[y-1, '상급종합']
        tge_y = ae_prev * idx
        ae_y = df_ae.loc[y, '상급종합']
        sum_tge += tge_y
        sum_ae += ae_y
        
    # 새로운 분모 약속: AE_2023 * (1 + SGR_2024)
    comp_2024 = sgr_calc._calc_sgr_components(y_next)
    sgr_idx_2024 = sgr_calc.calc_sgr_index(comp_2024, model='S1')['상급종합']
    denom_accum = ae_2023 * (1 + sgr_idx_2024) # 수정된 부분
    
    gap_accum = (sum_tge - sum_ae) / denom_accum
    
    # 3. 최종 PAF_2025
    paf_raw = (gap_short * 0.75) + (gap_accum * 0.33)
    paf_clipped = max(-0.05, min(0.05, paf_raw))
    
    print(f"=== [UAF_2025 상급종합병원 S1 수정 수식 상세 내역] ===")
    print(f"\n1. 단기 격차 (2023년)")
    print(f"  - TGE_2023: {ae_2022:,.2f} * {sgr_idx_2023:.6f} = {tge_2023:,.2f}")
    print(f"  - AE_2023: {ae_2023:,.2f}")
    print(f"  - 단기 Gap: ({tge_2023:,.2f} - {ae_2023:,.2f}) / {ae_2023:,.2f} = {gap_short:.6f}")
    
    print(f"\n2. 누적 격차 (2014-2023)")
    print(f"  - 10개년 TGE 합계: {sum_tge:,.2f}")
    print(f"  - 10개년 AE 합계: {sum_ae:,.2f}")
    print(f"  - 분모 (AE_2023 * (1 + SGR_2024)): ")
    print(f"    {ae_2023:,.2f} * (1 + {sgr_idx_2024:.6f}) = {ae_2023:,.2f} * {1+sgr_idx_2024:.6f} = {denom_accum:,.2f}")
    print(f"  - 누적 Gap: ({sum_tge:,.2f} - {sum_ae:,.2f}) / {denom_accum:,.2f} = {gap_accum:.6f}")
    
    print(f"\n3. 최종 PAF_2025 산출")
    print(f"  - ({gap_short:.6f} * 0.75) + ({gap_accum:.6f} * 0.33) = {paf_raw:.6f}")
    print(f"  - 백분율: {paf_raw*100:.4f}%")
    print(f"  - 최종 (Clipping 적용): {paf_clipped*100:.2f}%")

if __name__ == "__main__":
    debug_uaf_2025_s1_fixed()

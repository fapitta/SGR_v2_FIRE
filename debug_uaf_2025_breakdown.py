import pandas as pd
import numpy as np

def debug_uaf_2025_s1_tertiary():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    
    # 데이터 로드
    df_ae = pd.read_excel(EXCEL_FILE_PATH, sheet_name='진료비_실제', index_col=0)
    
    # SGR 계산기 초기화 (인덱스 획득용)
    from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator
    processor = DataProcessor(EXCEL_FILE_PATH)
    sgr_calc = SgrCalculator(processor.data, processor.HOSPITAL_TYPES)
    
    T = 2025
    y_recent = T - 2 # 2023
    
    # 1. 2023년 목표진료비 (TGE_2023)
    comp_2023 = sgr_calc._calc_sgr_components(2023)
    sgr_idx_2023 = sgr_calc.calc_sgr_index(comp_2023, model='S1')['상급종합']
    ae_2022 = df_ae.loc[2022, '상급종합']
    tge_2023 = ae_2022 * sgr_idx_2023
    
    # 2. 단기 격차 (Gap_2023)
    ae_2023 = df_ae.loc[2023, '상급종합']
    gap_short = (tge_2023 - ae_2023) / ae_2023
    
    # 3. 누적 격차 (2014 ~ 2023 : 10개년)
    sum_tge = 0
    sum_ae = 0
    details = []
    for y in range(2014, 2024):
        comp = sgr_calc._calc_sgr_components(y)
        idx = sgr_calc.calc_sgr_index(comp, model='S1')['상급종합']
        ae_prev = df_ae.loc[y-1, '상급종합']
        tge_y = ae_prev * idx
        ae_y = df_ae.loc[y, '상급종합']
        sum_tge += tge_y
        sum_ae += ae_y
        details.append({'연도': y, 'SGR_Idx': idx, 'AE_prev': ae_prev, 'TGE': tge_y, 'AE': ae_y})
    
    # 누적 분모 계산: AE_2023 * (1 + SGR_2024)
    comp_2024 = sgr_calc._calc_sgr_components(2024)
    sgr_idx_2024 = sgr_calc.calc_sgr_index(comp_2024, model='S1')['상급종합']
    denom_accum = ae_2023 * sgr_idx_2024
    
    gap_accum = (sum_tge - sum_ae) / denom_accum
    
    # 4. 최종 PAF_2025
    # 공식: 단기*0.75 + 누적*0.33
    paf_2025 = (gap_short * 0.75) + (gap_accum * 0.33)
    
    print(f"=== [UAF_2025 상급종합병원 현행(S1) 상세 산출 내역] ===")
    print(f"\n1. 단기 격차 반영 (최신자료 2023년)")
    print(f"  - 2022년 실제진료비 (AE): {ae_2022:,.2f}")
    print(f"  - 2023년 SGR 인덱스: {sgr_idx_2023:.6f}")
    print(f"  - 2023년 목표진료비 (TGE): {tge_2023:,.2f}")
    print(f"  - 2023년 실제진료비 (AE): {ae_2023:,.2f}")
    print(f"  - 단기 격차(Gap): ({tge_2023:,.2f} - {ae_2023:,.2f}) / {ae_2023:,.2f} = {gap_short:.6f}")
    
    print(f"\n2. 누적 격차 반영 (2014~2023년, 10개년)")
    print(f"  - 10개년 TGE 합계: {sum_tge:,.2f}")
    print(f"  - 10개년 AE 합계: {sum_ae:,.2f}")
    print(f"  - 2024년 SGR 인덱스: {sgr_idx_2024:.6f}")
    print(f"  - 분모 (AE_2023 * SGR_2024): {denom_accum:,.2f}")
    print(f"  - 누적 격차(Gap): ({sum_tge:,.2f} - {sum_ae:,.2f}) / {denom_accum:,.2f} = {gap_accum:.6f}")
    
    print(f"\n3. 최종 PAF_2025 (S1)")
    print(f"  - ({gap_short:.6f} * 0.75) + ({gap_accum:.6f} * 0.33) = {paf_2025:.6f}")
    print(f"  - 백분율 변환: {paf_2025*100:.2f}%")

if __name__ == "__main__":
    debug_uaf_2025_s1_tertiary()

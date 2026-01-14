import pandas as pd
import numpy as np

def debug_uaf_2025_s2_clinics():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator
    
    processor = DataProcessor(EXCEL_FILE_PATH)
    sgr_calc = SgrCalculator(processor.data, processor.HOSPITAL_TYPES)
    df_ae = processor.data['df_expenditure']
    
    TARGET_HOS = '의원'
    T = 2025
    # S2 수식: (T-2)*0.5 + (T-3)*0.3 + (T-4)*0.2
    lags = [2, 3, 4]
    weights = [0.5, 0.3, 0.2]
    
    results = []
    total_uaf = 0.0
    
    print(f"=== [UAF_2025 의원(Clinics) SGR 개선모형(S2) 상세 산출 내역] ===")
    
    for lag, weight in zip(lags, weights):
        y = T - lag
        # S2 모델 components 계산
        comp = sgr_calc._calc_sgr_components(y)
        sgr_idx_s2 = sgr_calc.calc_sgr_index(comp, model='S2')[TARGET_HOS]
        
        # TGE_y = AE_{y-1} * SGR_idx_s2
        ae_prev = df_ae.loc[y - 1, TARGET_HOS]
        tge_y = ae_prev * sgr_idx_s2
        ae_y = df_ae.loc[y, TARGET_HOS]
        
        # Gap_y = (TGE_y - AE_y) / AE_y
        gap_y = (tge_y - ae_y) / ae_y
        weighted_gap = gap_y * weight
        total_uaf += weighted_gap
        
        results.append({
            '시차': f'T-{lag}({y}년)',
            '가중치': weight,
            'SGR_S2_Idx': sgr_idx_s2,
            'AE_prev': ae_prev,
            'TGE_S2': tge_y,
            'AE_y': ae_y,
            'Gap': gap_y
        })

    # 의원 기준 상세 출력
    for res in results:
        print(f"\n[{res['시차']} 가중치 {res['가중치']}]")
        print(f"  - {res['시차']} SGR(S2) 인덱스: {res['SGR_S2_Idx']:.6f}")
        print(f"  - 목표진료비(TGE): {res['AE_prev']:,.2f} * {res['SGR_S2_Idx']:.6f} = {res['TGE_S2']:,.2f}")
        print(f"  - 실제진료비(AE): {res['AE_y']:,.2f}")
        print(f"  - 격차(Gap): ({res['TGE_S2']:,.2f} - {res['AE_y']:,.2f}) / {res['AE_y']:,.2f} = {res['Gap']:.6f}")
        print(f"  - 가중 격차: {res['Gap']:.6f} * {res['가중치']} = {res['Gap']*res['가중치']:.6f}")

    print(f"\n[최종 UAF_2025 (S2)]")
    print(f"  - 합계: {total_uaf:.6f}")
    print(f"  - 백분율: {total_uaf*100:.2f}%")

if __name__ == "__main__":
    debug_uaf_2025_s2_clinics()

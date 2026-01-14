from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator
import pandas as pd

def debug_calculation():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    engine_data = processor.raw_data
    hospital_types = ['상급종합', '병원']
    
    sgr_calc = SgrCalculator(engine_data, hospital_types)
    
    print("\n=== 2020년 SGR 구성요소 상세 분석 (상급종합 vs 병원) ===")
    
    year = 2020
    comp = sgr_calc._calc_sgr_components(year)
    
    # Common Macros
    g_s1 = comp['g_s1']
    p_s1 = comp['p_s1']
    
    print(f"\n[공통 거시지표]")
    print(f"1인당 실질GDP 증가율 (g_s1): {g_s1:.6f} (SGR계산용: {g_s1:.6f})")
    print(f"건보대상자 증가율 (p_s1): {p_s1:.6f} (SGR계산용: {p_s1:.6f})")
    
    print(f"\n[유형별 지표 및 결과]")
    for htype in hospital_types:
        l_val = comp['l'][htype]
        r_val = comp['r'][htype]
        
        # Breakdown of R (Revaluation)
        reval_curr = engine_data['df_sgr_reval'].loc[year, htype]
        reval_prev = engine_data['df_sgr_reval'].loc[year-1, htype]
        
        print(f"\n>> {htype}:")
        print(f"  - 법과제도변화 (L): {l_val:.6f}")
        print(f"  - 환산지수 변화 (R): {r_val:.6f} ( {reval_curr} / {reval_prev} )")
        
        sgr_s1 = g_s1 * p_s1 * l_val * r_val
        print(f"  = SGR(S1) 계산값: {sgr_s1 * 100 - 100:.2f}% (지수: {sgr_s1:.6f})")
        print(f"    (Calculation: {g_s1:.6f} * {p_s1:.6f} * {l_val:.6f} * {r_val:.6f})")

if __name__ == "__main__":
    debug_calculation()

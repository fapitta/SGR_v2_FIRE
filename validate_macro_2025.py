import pandas as pd
import numpy as np
from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator, FinalRateCalculator, MeiCalculator

def validate_macro_2025():
    processor = DataProcessor('h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx')
    data = processor.data
    hospital_types = processor.HOSPITAL_TYPES
    group_mapping = processor.GROUP_MAPPING
    
    # 2025년 기준 (T-1 = 2024, T-2 = 2023)
    sgr_calc = SgrCalculator(data, hospital_types)
    comp_2024 = sgr_calc._calc_sgr_components(2024)
    
    mei_calc = MeiCalculator(data, hospital_types)
    df_mei = mei_calc.calc_mei_index_by_year(2025) # MEI는 T-2(2023) 물가 반영
    
    final_calc = FinalRateCalculator(data, group_mapping)
    _, df_macro = final_calc.calc_macro_final_rate(df_mei, comp_2024, 2025)
    
    print("--- [2025년 거시지표 모형 검산 결과 (%)] ---")
    print(f"2023년 실질 GDP 총액 증가율: {(comp_2024['gdp_total_idx']-1)*100:.4f}%")
    print(f"2023년 MEI 평균 증가율: {(df_mei['평균'].mean()-1)*100:.4f}% (종별 가중치 적용 전)")
    
    res_pct = ((df_macro - 1) * 100).round(2)
    print("\n유형별 최종 조정률 (%):")
    print(res_pct)

if __name__ == "__main__":
    validate_macro_2025()

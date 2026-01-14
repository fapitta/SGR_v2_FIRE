import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator

def calculate_uaf_history():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    # 구하고자 하는 환산지수 타겟 연도: 2020-2027
    TARGET_YEARS = range(2020, 2028)
    
    processor = DataProcessor(EXCEL_FILE_PATH)
    data = processor.data
    hospital_types = processor.HOSPITAL_TYPES
    sgr_calc = SgrCalculator(data, hospital_types)
    
    uaf_s1_final = {}
    uaf_s2_final = {}

    for T in TARGET_YEARS:
        # SgrCalculator에 구현된 수정된 로직 직접 호출
        paf_s1 = sgr_calc.calc_paf_s1(T)
        paf_s2 = sgr_calc.calc_paf_s2(T)
        
        uaf_s1_final[f"UAF_{T}"] = paf_s1
        uaf_s2_final[f"UAF_{T}"] = paf_s2

    # 결과 정리
    df_uaf_s1 = pd.DataFrame(uaf_s1_final).T * 100 # % 단위
    df_uaf_s2 = pd.DataFrame(uaf_s2_final).T * 100 # % 단위
    
    print("\n=== [S1] 현행 모형 UAF 결과 (% 단위, 2020-2027) ===")
    print(df_uaf_s1.round(2))
    
    print("\n=== [S2] 개선 모형 UAF 결과 (% 단위, 2020-2027) ===")
    print(df_uaf_s2.round(2))

    # 엑셀 저장
    with pd.ExcelWriter('h:/병원환산지수연구_2027년/UAF_산출_최종결과_수정본.xlsx') as writer:
        df_uaf_s1.to_excel(writer, sheet_name='UAF_S1_현행')
        df_uaf_s2.to_excel(writer, sheet_name='UAF_S2_개선')
    print(f"\n✅ 수정이 반영된 UAF 결과가 'UAF_산출_최종결과_수정본.xlsx'로 저장되었습니다.")

if __name__ == "__main__":
    calculate_uaf_history()

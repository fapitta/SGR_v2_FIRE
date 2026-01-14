import pandas as pd
import numpy as np
import warnings

# 경고 무시 설정
warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, MeiCalculator

def main():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    TARGET_YEAR = 2025 # 2025년도 환산지수 조정률을 위해 2023년도 MEI (T-2) 계산

    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        
        mei_calc = MeiCalculator(data, hospital_types)
        df_mei_16 = mei_calc.calc_mei_index_by_year(TARGET_YEAR)
        
        if df_mei_16 is not None:
            # 퍼센트 변화율로 변환 (지수 - 1) * 100
            df_mei_pct = (df_mei_16 - 1) * 100
            
            print("--- 2023년도 의료물가지수 (MEI) 결과 (단위: %) ---")
            print(df_mei_pct.round(4).to_string())
            
            # 시나리오 리스트와 통계량 리스트 확인
            cols = df_mei_pct.columns.tolist()
            scenarios = [c for c in cols if c not in ['평균', '최대', '최소', '중위수']]
            stats = ['평균', '최대', '최소', '중위수']
            
            print("\n--- 12가지 시나리오 ---")
            print(scenarios)
            print("\n--- 4가지 통계량 ---")
            print(stats)
        else:
            print("MEI 계산 결과가 없습니다. 데이터를 확인하세요.")
            
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()

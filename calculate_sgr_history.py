import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator

def main():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    YEAR_RANGE = range(2015, 2027)

    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        sgr_calc = SgrCalculator(data, hospital_types)
        
        results_s1 = []
        results_s2 = []
        
        for year in YEAR_RANGE:
            components = sgr_calc._calc_sgr_components(year)
            if components:
                idx_s1 = sgr_calc.calc_sgr_index(components, model='S1')
                idx_s2 = sgr_calc.calc_sgr_index(components, model='S2')
                
                # 병원 종별 중 '상급종합' 대표값만 일단 수집하거나 전체 평균을 낼 수 있음
                # 여기서는 모든 종별의 평균 (사실 SGR 인덱스는 종별로 같음, reval_idx가 종별로 다를 수 있으니 주의)
                results_s1.append(idx_s1)
                results_s2.append(idx_s2)
            else:
                results_s1.append(pd.Series(np.nan, index=hospital_types))
                results_s2.append(pd.Series(np.nan, index=hospital_types))

        # 데이터프레임 구성 (행: 연도, 열: 종별)
        df_s1 = pd.DataFrame(results_s1, index=YEAR_RANGE)
        df_s2 = pd.DataFrame(results_s2, index=YEAR_RANGE)

        print("\n=== [S1] 현행 SGR 모형 인덱스 (2015-2026) ===")
        print(df_s1.round(4))
        
        print("\n=== [S2] 개선 SGR 모형 인덱스 (2015-2026) ===")
        print(df_s2.round(4))

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()

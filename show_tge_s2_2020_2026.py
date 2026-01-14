import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator

def main():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    YEAR_RANGE = range(2020, 2027) # 2020-2026

    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        sgr_calc = SgrCalculator(data, hospital_types)
        
        tge_s2_results = []
        
        for year in YEAR_RANGE:
            # SGR S2 인덱스 산출 (이미 수정된 '약속' 로직 반영됨)
            components = sgr_calc._calc_sgr_components(year)
            if components:
                idx_s2 = sgr_calc.calc_sgr_index(components, model='S2')
                
                # TGE_t = AE_{t-1} * SGR_t
                try:
                    ae_prev = data['df_expenditure'].loc[year - 1]
                    tge_s2 = ae_prev * idx_s2
                    tge_s2_results.append(tge_s2)
                except KeyError:
                    tge_s2_results.append(pd.Series(np.nan, index=hospital_types))
            else:
                tge_s2_results.append(pd.Series(np.nan, index=hospital_types))

        # 데이터프레임 구성
        df_tge_s2 = pd.DataFrame(tge_s2_results, index=YEAR_RANGE)
        
        # 10개 종별 전체 출력
        print("\n=== [S2] 개선 SGR 모형 목표진료비 (TGE, 2020-2026) ===")
        # 컬럼 순서 조정 (보기 좋게)
        cols = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
        print(df_tge_s2[cols].round(1).to_string())

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()

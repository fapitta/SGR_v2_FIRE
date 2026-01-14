import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator

def main():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    # 2014년부터 2027년까지 산출
    YEAR_RANGE = range(2014, 2028)

    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        sgr_calc = SgrCalculator(data, hospital_types)
        
        tge_s1_results = []
        tge_s2_results = []
        
        for year in YEAR_RANGE:
            # SGR 인덱스 산출
            components = sgr_calc._calc_sgr_components(year)
            if components:
                idx_s1 = sgr_calc.calc_sgr_index(components, model='S1')
                idx_s2 = sgr_calc.calc_sgr_index(components, model='S2')
                
                # TGE_t = AE_{t-1} * SGR_t
                try:
                    ae_prev = data['df_expenditure'].loc[year - 1]
                    tge_s1 = ae_prev * idx_s1
                    tge_s2 = ae_prev * idx_s2
                    
                    tge_s1_results.append(tge_s1)
                    tge_s2_results.append(tge_s2)
                except KeyError:
                    # 전년도 실제 진료비가 없으면 계산 불가
                    tge_s1_results.append(pd.Series(np.nan, index=hospital_types))
                    tge_s2_results.append(pd.Series(np.nan, index=hospital_types))
            else:
                tge_s1_results.append(pd.Series(np.nan, index=hospital_types))
                tge_s2_results.append(pd.Series(np.nan, index=hospital_types))

        # 데이터프레임 구성 (행: 연도, 열: 종별)
        df_tge_s1 = pd.DataFrame(tge_s1_results, index=YEAR_RANGE)
        df_tge_s2 = pd.DataFrame(tge_s2_results, index=YEAR_RANGE)

        print("\n=== [S1] 현행 모형 목표진료비 (TGE) (2014-2027) ===")
        print(df_tge_s1.round(0)) # 진료비이므로 소수점 제거하고 출력
        
        print("\n=== [S2] 개선 모형 목표진료비 (TGE) (2014-2027) ===")
        print(df_tge_s2.round(0))

        # 엑셀로 저장하여 확인 가능하게 함
        with pd.ExcelWriter('h:/병원환산지수연구_2027년/TGE_산출_결과.xlsx') as writer:
            df_tge_s1.to_excel(writer, sheet_name='목표진료비_S1_현행')
            df_tge_s2.to_excel(writer, sheet_name='목표진료비_S2_개선')
        print(f"\n✅ TGE 결과가 'TGE_산출_결과.xlsx' 파일로 저장되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    main()

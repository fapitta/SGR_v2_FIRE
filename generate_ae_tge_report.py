import pandas as pd
import numpy as np
import warnings
import io

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator

def generate_full_tge_ae_report():
    """
    실제진료비(AE), 현행모형 목표진료비(TGE_S1), 개선모형 목표진료비(TGE_S2)를
    종별/연도별로 합쳐서 엑셀 리포트를 생성합니다.
    """
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    OUTPUT_FILE_PATH = 'h:/병원환산지수연구_2027년/진료비_상세_분석_리포트.xlsx'
    
    # 2014년부터 2026년까지 (2027년은 SGR 데이터 부족으로 제외 가능성 있음)
    YEAR_RANGE = range(2014, 2027)

    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        sgr_calc = SgrCalculator(data, hospital_types)
        
        ae_actual = data['df_expenditure']
        
        tge_s1_list = []
        tge_s2_list = []
        
        for year in YEAR_RANGE:
            components = sgr_calc._calc_sgr_components(year)
            if components:
                idx_s1 = sgr_calc.calc_sgr_index(components, model='S1')
                idx_s2 = sgr_calc.calc_sgr_index(components, model='S2')
                
                try:
                    ae_prev = ae_actual.loc[year - 1]
                    tge_s1_list.append(ae_prev * idx_s1)
                    tge_s2_list.append(ae_prev * idx_s2)
                except KeyError:
                    tge_s1_list.append(pd.Series(np.nan, index=hospital_types))
                    tge_s2_list.append(pd.Series(np.nan, index=hospital_types))
            else:
                tge_s1_list.append(pd.Series(np.nan, index=hospital_types))
                tge_s2_list.append(pd.Series(np.nan, index=hospital_types))

        # 데이터프레임 구성
        df_tge_s1 = pd.DataFrame(tge_s1_list, index=YEAR_RANGE)
        df_tge_s2 = pd.DataFrame(tge_s2_list, index=YEAR_RANGE)
        df_ae = ae_actual.loc[YEAR_RANGE]

        # 엑셀 파일 생성
        with pd.ExcelWriter(OUTPUT_FILE_PATH, engine='openpyxl') as writer:
            # 1. 실제 진료비 (AE)
            df_ae.to_excel(writer, sheet_name='1_실제진료비(AE)')
            
            # 2. 현행모형 목표진료비 (TGE_S1)
            df_tge_s1.to_excel(writer, sheet_name='2_목표진료비_현행(S1)')
            
            # 3. 개선모형 목표진료비 (TGE_S2)
            df_tge_s2.to_excel(writer, sheet_name='3_목표진료비_개선(S2)')
            
            # 4. 종합 비교 (상급종합 기준 예시)
            pivot_data = []
            for year in YEAR_RANGE:
                for htype in hospital_types:
                    pivot_data.append({
                        '연도': year,
                        '종별': htype,
                        '실제진료비(AE)': df_ae.loc[year, htype],
                        '목표진료비(S1)': df_tge_s1.loc[year, htype],
                        '목표진료비(S2)': df_tge_s2.loc[year, htype],
                        '격차율(S1%)': (df_tge_s1.loc[year, htype] - df_ae.loc[year, htype]) / df_ae.loc[year, htype] * 100,
                        '격차율(S2%)': (df_tge_s2.loc[year, htype] - df_ae.loc[year, htype]) / df_ae.loc[year, htype] * 100
                    })
            df_comparison = pd.DataFrame(pivot_data)
            df_comparison.to_excel(writer, sheet_name='4_종합비교_데이터', index=False)

        print(f"\n✅ 진료비 분석 데이터가 '{OUTPUT_FILE_PATH}' 파일로 생성되었습니다.")
        
        # 화면 출력 (최근 5개년 요약)
        print("\n[최근 5개년 상급종합병원 요약]")
        summary = df_comparison[df_comparison['종별'] == '상급종합'].tail(5)
        print(summary[['연도', '실제진료비(AE)', '목표진료비(S1)', '목표진료비(S2)']].round(1).to_string(index=False))

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    generate_full_tge_ae_report()

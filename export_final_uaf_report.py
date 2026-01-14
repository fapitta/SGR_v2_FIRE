import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator

def export_uaf_full_report():
    """
    현행(S1) 및 개선(S2) 모형의 UAF(2020-2027)를 
    종별/연도별로 정리하여 엑셀 파일로 출력합니다.
    """
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    OUTPUT_FILE_PATH = 'h:/병원환산지수연구_2027년/SGR_UAF_최종_분석_표.xlsx'
    
    TARGET_YEARS = range(2020, 2028)
    
    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        sgr_calc = SgrCalculator(data, hospital_types)
        
        uaf_s1_list = []
        uaf_s2_list = []
        
        for T in TARGET_YEARS:
            # SgrCalculator에 업데이트된 로직 (클리핑 제거, 수식 수정 반영) 호출
            paf_s1 = sgr_calc.calc_paf_s1(T)
            paf_s2 = sgr_calc.calc_paf_s2(T)
            
            uaf_s1_list.append(paf_s1)
            uaf_s2_list.append(paf_s2)
            
        # 데이터프레임 생성 (행: 연도, 열: 종별)
        df_uaf_s1 = pd.DataFrame(uaf_s1_list, index=[f"UAF_{T}" for T in TARGET_YEARS]) * 100
        df_uaf_s2 = pd.DataFrame(uaf_s2_list, index=[f"UAF_{T}" for T in TARGET_YEARS]) * 100
        
        # 가독성을 위한 전치(T) 지원 (행: 종별, 열: 연도)
        df_uaf_s1_T = df_uaf_s1.T
        df_uaf_s2_T = df_uaf_s2.T

        # 엑셀 파일 저장
        with pd.ExcelWriter(OUTPUT_FILE_PATH, engine='openpyxl') as writer:
            # 1. 현행 모형 (S1) - 연도별
            df_uaf_s1.to_excel(writer, sheet_name='S1_현행_연도별')
            # 2. 현행 모형 (S1) - 종별
            df_uaf_s1_T.to_excel(writer, sheet_name='S1_현행_종별')
            
            # 3. 개선 모형 (S2) - 연도별
            df_uaf_s2.to_excel(writer, sheet_name='S2_개선_연도별')
            # 4. 개선 모형 (S2) - 종별
            df_uaf_s2_T.to_excel(writer, sheet_name='S2_개선_종별')
            
            # 5. 요약 비교 (상급종합병원 예시)
            comparison = pd.DataFrame({
                '연도': [f"{T}년용" for T in TARGET_YEARS],
                '현행(S1) UI_상급': df_uaf_s1['상급종합'],
                '개선(S2) UI_상급': df_uaf_s2['상급종합'],
                '현행(S1) UI_의원': df_uaf_s1['의원'],
                '개선(S2) UI_의원': df_uaf_s2['의원']
            })
            comparison.to_excel(writer, sheet_name='주요종별_비교', index=False)

        print(f"\n✅ UAF 분석 리포트가 '{OUTPUT_FILE_PATH}' 파일로 생성되었습니다.")
        
        # 화면에 주요 결과 출력
        print("\n[UAF_2025 종별 산출 결과 요약 (%)]")
        summary_2025 = pd.DataFrame({
            '현행(S1)': df_uaf_s1.loc['UAF_2025'],
            '개선(S2)': df_uaf_s2.loc['UAF_2025']
        })
        print(summary_2025.round(2))

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    export_uaf_full_report()

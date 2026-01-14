import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator, MeiCalculator

def calculate_cf_2025_validation():
    """
    2025년 종별 환산지수 조정률(CF_2025) 산출 및 검증
    공식: CF_2025 = MEI_2023_index * (1 + UAF_2025)
    """
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    TARGET_YEAR = 2025
    
    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        
        # 1. MEI 산출 (2025년용 -> 2023년 데이터 기반)
        # 결과: 10개 종(행) x 16개 시나리오(열) DataFrame
        mei_calc = MeiCalculator(data, hospital_types)
        df_mei_2023_idx = mei_calc.calc_mei_index_by_year(TARGET_YEAR)
        
        # 2. UAF_2025 산출 (S1, S2)
        sgr_calc = SgrCalculator(data, hospital_types)
        uaf_s1_2025 = sgr_calc.calc_paf_s1(TARGET_YEAR)
        uaf_s2_2025 = sgr_calc.calc_paf_s2(TARGET_YEAR)
        
        # 3. 최종 조정률(CF) 산출
        # CF_index = MEI_index * (1 + UAF)
        # 행렬 연산을 위해 UAF를 확장하거나 순회 계산
        
        cf_s1_results = []
        cf_s2_results = []
        
        for scenario in df_mei_2023_idx.columns:
            mei_idx = df_mei_2023_idx[scenario]
            
            # S1 기반 CF
            cf_val_s1 = mei_idx * (1 + uaf_s1_2025)
            cf_s1_results.append(cf_val_s1)
            
            # S2 기반 CF
            cf_val_s2 = mei_idx * (1 + uaf_s2_2025)
            cf_s2_results.append(cf_val_s2)
            
        df_cf_s1 = pd.concat(cf_s1_results, axis=1)
        df_cf_s1.columns = df_mei_2023_idx.columns
        
        df_cf_s2 = pd.concat(cf_s2_results, axis=1)
        df_cf_s2.columns = df_mei_2023_idx.columns
        
        # 4. 결과 출력 및 저장
        # 퍼센트 변환 함수
        def to_pct(df): return (df - 1) * 100

        print(f"\n=== [2025년 최종 환산지수 조정률(CF) 검증 - S1 현행 모형] ===")
        print(f"(단위: %, 16개 시나리오)")
        # 상급종합병원과 의원 결과만 먼저 확인
        print(to_pct(df_cf_s1).loc[['상급종합', '의원']].round(2))
        
        print(f"\n=== [2025년 최종 환산지수 조정률(CF) 검증 - S2 개선 모형] ===")
        print(f"(단위: %, 16개 시나리오)")
        print(to_pct(df_cf_s2).loc[['상급종합', '의원']].round(2))

        # 엑셀 저장
        with pd.ExcelWriter('h:/병원환산지수연구_2027년/CF_2025_검증_리포트.xlsx') as writer:
            to_pct(df_cf_s1).to_excel(writer, sheet_name='CF_2025_S1_현행')
            to_pct(df_cf_s2).to_excel(writer, sheet_name='CF_2025_S2_개선')
            
            # 지수(Index) 형태도 저장
            df_cf_s1.to_excel(writer, sheet_name='CF_2025_S1_Index')
            df_cf_s2.to_excel(writer, sheet_name='CF_2025_S2_Index')
            
            # PAF와 MEI 원본도 참고용으로 저장
            pd.DataFrame({'UAF_S1': uaf_s1_2025, 'UAF_S2': uaf_s2_2025}).to_excel(writer, sheet_name='참고_UAF_2025')
            df_mei_2023_idx.to_excel(writer, sheet_name='참고_MEI_2023_Index')

        print(f"\n✅ CF_2025 검증 리포트가 'CF_2025_검증_리포트.xlsx'로 저장되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    calculate_cf_2025_validation()

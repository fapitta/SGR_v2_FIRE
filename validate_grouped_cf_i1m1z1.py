import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator, MeiCalculator, FinalRateCalculator

def validate_grouped_cf_2025_i1m1z1():
    """
    2025년도 5개 그룹 통합 CF 검증
    - 시나리오: I1M1Z1 (인건비1, 관리비1, 재료비1)
    - 가중치: 2023년 실제 진료비 비중
    """
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    TARGET_YEAR = 2025
    SCENARIO = 'I1M1Z1'
    
    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        group_mapping = processor.GROUP_MAPPING
        
        # 1. 기초 값 산출 (10개 종별)
        mei_calc = MeiCalculator(data, hospital_types)
        df_mei = mei_calc.calc_mei_index_by_year(TARGET_YEAR)
        mei_i1m1z1 = df_mei[SCENARIO] # 10개 종의 I1M1Z1 지수
        
        sgr_calc = SgrCalculator(data, hospital_types)
        uaf_s1 = sgr_calc.calc_paf_s1(TARGET_YEAR)
        uaf_s2 = sgr_calc.calc_paf_s2(TARGET_YEAR)
        
        df_rel_value = data['df_rel_value']
        try:
            rv_idx = df_rel_value.loc[TARGET_YEAR - 1].reindex(hospital_types).fillna(1.0)
        except KeyError:
            rv_idx = pd.Series(1.0, index=hospital_types)
            
        # 2. 10개 종별 CF 지수 산출 (I1M1Z1)
        # S1 = MEI * (1 + UAF)
        cf_s1_10 = mei_i1m1z1 * (1 + uaf_s1)
        # S2 = MEI * (1 + UAF) - (RV - 1)
        cf_s2_10 = (mei_i1m1z1 * (1 + uaf_s2)) - (rv_idx - 1)
        
        # 3. 그룹 통합 (2023년 진료비 가중치)
        # DataFrame 형태로 변환하여 FinalRateCalculator의 로직 활용
        df_cf_10_formatted = pd.DataFrame({SCENARIO: cf_s1_10}) # S1용 임시 DF
        final_calc = FinalRateCalculator(data, group_mapping)
        
        group_s1_res = final_calc._group_and_weight_average(pd.DataFrame({SCENARIO: cf_s1_10}), TARGET_YEAR)
        group_s2_res = final_calc._group_and_weight_average(pd.DataFrame({SCENARIO: cf_s2_10}), TARGET_YEAR)
        
        # 4. 결과 출력
        print(f"=== [2025년 5개 그룹별 통합 CF 검증] ===")
        print(f"시나리오: {SCENARIO} (인건비1, 관리비1, 재료비1)")
        print(f"가중치 기준: 2023년 실제 진료비 비중\n")
        
        results_summary = pd.DataFrame({
            '현행_S1_지수': group_s1_res[SCENARIO],
            '현행_S1_조정률(%)': (group_s1_res[SCENARIO] - 1) * 100,
            '개선_S2_지수': group_s2_res[SCENARIO],
            '개선_S2_조정률(%)': (group_s2_res[SCENARIO] - 1) * 100
        })
        
        print(results_summary.round(4))
        
        # 병원 그룹 상세 비중 확인 (재출력)
        ae_2023 = data['df_expenditure'].loc[2023]
        for group, members in group_mapping.items():
            total_ae = ae_2023[members].sum()
            print(f"\n[{group}] 그룹 내부 비중:")
            for m in members:
                share = ae_2023[m] / total_ae
                val_s1 = (cf_s1_10[m] - 1) * 100
                print(f"  - {m}: {share*100:.2f}% (개별 조정률: {val_s1:.2f}%)")

    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    validate_grouped_cf_2025_i1m1z1()

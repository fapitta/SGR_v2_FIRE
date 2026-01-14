import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator, MeiCalculator, FinalRateCalculator

def calculate_grouped_cf_report():
    """
    환산지수 조정률(CF)을 5개 그룹으로 통합하여 산출
    - 가중치: target_year - 2년의 실제진료비(AE) 비중
    - 대상: 2020-2027
    """
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    YEAR_RANGE = range(2020, 2028)
    
    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        group_mapping = processor.GROUP_MAPPING
        
        sgr_calc = SgrCalculator(data, hospital_types)
        mei_calc = MeiCalculator(data, hospital_types)
        final_calc = FinalRateCalculator(data, group_mapping)
        
        df_rel_value = data['df_rel_value']
        df_ae = data['df_expenditure']
        
        all_grouped_s1 = []
        all_grouped_s2 = []

        print("--- 🚀 그룹별 CF 산출 시작 (2020-2027) ---")
        
        for target_year in YEAR_RANGE:
            # 1. MEI 및 UAF 산출 (10개 종별 기초 데이터)
            df_mei_idx = mei_calc.calc_mei_index_by_year(target_year)
            if df_mei_idx is None: continue
            
            uaf_s1 = sgr_calc.calc_paf_s1(target_year)
            uaf_s2 = sgr_calc.calc_paf_s2(target_year)
            
            try:
                rv_idx = df_rel_value.loc[target_year - 1].reindex(hospital_types).fillna(1.0)
            except KeyError:
                rv_idx = pd.Series(1.0, index=hospital_types)
            
            # 2. 10개 종별 CF 산 산출 (Index 형태)
            # S1_idx = MEI * (1 + UAF_S1)
            cf_s1_10_idx = df_mei_idx.multiply(1 + uaf_s1, axis=0)
            
            # S2_idx = MEI * (1 + UAF_S2) - (RV_idx - 1)
            base_s2_10_idx = df_mei_idx.multiply(1 + uaf_s2, axis=0)
            cf_s2_10_idx = base_s2_10_idx.sub(rv_idx - 1, axis=0)
            
            # 3. 그룹핑 (T-2년 진료비 가중치 적용)
            # final_calc._group_and_weight_average(df_rates, target_year) 호출
            # 이 함수는 (인덱스 - 1) * 가중치 의 합 + 1 을 반환하여 지수 형태를 유지함
            group_s1 = final_calc._group_and_weight_average(cf_s1_10_idx, target_year)
            group_s2 = final_calc._group_and_weight_average(cf_s2_10_idx, target_year)
            
            # 평균 시나리오만 추출하여 리스트에 저장
            s1_avg_pct = (group_s1['평균'] - 1) * 100
            s2_avg_pct = (group_s2['평균'] - 1) * 100
            
            s1_avg_pct.name = f"{target_year}"
            s2_avg_pct.name = f"{target_year}"
            
            all_grouped_s1.append(s1_avg_pct)
            all_grouped_s2.append(s2_avg_pct)
            
            # 검산용 2025년 데이터 상세 저장
            if target_year == 2025:
                res_2025_s1 = group_s1
                res_2025_s2 = group_s2
                weight_2023 = df_ae.loc[2023].reindex(hospital_types)

        # 결과 데이터프레임 (행: 연도, 열: 5개 그룹)
        df_final_s1 = pd.concat(all_grouped_s1, axis=1).T
        df_final_s2 = pd.concat(all_grouped_s2, axis=1).T
        
        print("\n=== [S1 현행] 5개 그룹별 환산지수 조정률 추이 (평균, %) ===")
        print(df_final_s1.round(2))
        
        print("\n=== [S2 개선] 5개 그룹별 환산지수 조정률 추이 (평균, %) ===")
        print(df_final_s2.round(2))
        
        # 2025년 검산 상세 정보 출력
        print("\n=== [검산용 2025년 종별 -> 그룹 통합 상세 (S1 기준)] ===")
        # 병원 그룹 예시 (상급종합, 종합병원, 병원, 요양병원)
        hosp_group_members = group_mapping['병원']
        weights_hosp = weight_2023[hosp_group_members]
        weights_hosp_norm = weights_hosp / weights_hosp.sum()
        
        print(f" 병원 그룹 가중치 (2023년 실적 비중):")
        for m in hosp_group_members:
            print(f"  - {m}: {weights_hosp_norm[m]*100:.2f}%")

        # 엑셀 저장
        with pd.ExcelWriter('h:/병원환산지수연구_2027년/CF_그룹별_통합_리포트.xlsx') as writer:
            df_final_s1.to_excel(writer, sheet_name='S1_통합_조정률(%)')
            df_final_s2.to_excel(writer, sheet_name='S2_통합_조정률(%)')
            
            # 2025년 16개 시나리오 상세
            (res_2025_s1 - 1).multiply(100).to_excel(writer, sheet_name='2025_S1_그룹별_시나리오(%)')
            (res_2025_s2 - 1).multiply(100).to_excel(writer, sheet_name='2025_S2_그룹별_시나리오(%)')
            
        print(f"\n✅ 그룹별 통합 리포트가 'CF_그룹별_통합_리포트.xlsx'로 생성되었습니다.")

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    calculate_grouped_cf_report()

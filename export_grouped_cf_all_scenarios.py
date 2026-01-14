import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator, MeiCalculator, FinalRateCalculator

def export_grouped_cf_full_scenarios():
    """
    2020-2027 전 연도 유형별(5개) 환산지수 조정률(CF) 상세 리포트
    - 16개 MEI 시나리오 모두 포함
    - 연도별 추이 및 등위(Rank) 계산 포함
    """
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    OUTPUT_FILE_PATH = 'h:/병원환산지수연구_2027년/SGR_CF_유형별_최종_분석표.xlsx'
    YEAR_RANGE = range(2020, 2028)
    
    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        group_mapping = processor.GROUP_MAPPING
        group_names = list(group_mapping.keys())
        
        sgr_calc = SgrCalculator(data, hospital_types)
        mei_calc = MeiCalculator(data, hospital_types)
        final_calc = FinalRateCalculator(data, group_mapping)
        df_rel_value = data['df_rel_value']
        
        # 통합 결과를 담을 딕셔너리
        results_s1_rate = {} # {year: DF(5groups x 16scenarios)}
        results_s2_rate = {}
        results_s1_idx = {}
        results_s2_idx = {}

        print("--- 🚀 전 연도/전 시나리오 유형별 통합 CF 산출 시작 ---")
        
        for target_year in YEAR_RANGE:
            # 1. MEI 및 UAF 산출 (10개 종별)
            df_mei_idx = mei_calc.calc_mei_index_by_year(target_year)
            if df_mei_idx is None: continue
            
            uaf_s1 = sgr_calc.calc_paf_s1(target_year)
            uaf_s2 = sgr_calc.calc_paf_s2(target_year)
            
            try:
                rv_idx = df_rel_value.loc[target_year - 1].reindex(hospital_types).fillna(1.0)
            except KeyError:
                rv_idx = pd.Series(1.0, index=hospital_types)
            
            # 2. 10개 종별 CF 산출
            cf_s1_10_idx = df_mei_idx.multiply(1 + uaf_s1, axis=0)
            base_s2_10_idx = df_mei_idx.multiply(1 + uaf_s2, axis=0)
            cf_s2_10_idx = base_s2_10_idx.sub(rv_idx - 1, axis=0)
            
            # 3. 5개 그룹 통합 (T-2 가중치)
            group_s1_idx = final_calc._group_and_weight_average(cf_s1_10_idx, target_year)
            group_s2_idx = final_calc._group_and_weight_average(cf_s2_10_idx, target_year)
            
            # 지수 및 퍼센트 저장
            results_s1_idx[target_year] = group_s1_idx
            results_s2_idx[target_year] = group_s2_idx
            results_s1_rate[target_year] = (group_s1_idx - 1) * 100
            results_s2_rate[target_year] = (group_s2_idx - 1) * 100

        # 엑셀 저장
        with pd.ExcelWriter(OUTPUT_FILE_PATH, engine='openpyxl') as writer:
            # 모델별 전 시나리오 시트 생성
            for model_name, data_dict in [('S1_현행', results_s1_rate), ('S2_개선', results_s2_rate)]:
                # 연도별로 시트를 만들지, 하나에 합칠지 고민 -> 연도별 상세 시트
                for year in YEAR_RANGE:
                    if year in data_dict:
                        data_dict[year].to_excel(writer, sheet_name=f'{model_name}_{year}년')

            # 전 연도 추이 및 등위 요약 (평균 시나리오 기준)
            for model_name, data_dict in [('S1_현행', results_s1_rate), ('S2_개선', results_s2_rate)]:
                summary_df = pd.DataFrame(index=group_names)
                for year in YEAR_RANGE:
                    if year in data_dict:
                        summary_df[f"{year}년"] = data_dict[year]['평균']
                
                # 등급(Rank) 계산: 각 연도별로 어떤 유형이 가장 높은지/낮은지 (높은것이 1등)
                rank_df = summary_df.rank(ascending=False, axis=0)
                
                summary_df.to_excel(writer, sheet_name=f'{model_name}_평균추이')
                rank_df.to_excel(writer, sheet_name=f'{model_name}_등위추이')

        print(f"\n✅ 유형별 통합 전 시나리오 리포트가 '{OUTPUT_FILE_PATH}' 파일로 생성되었습니다.")
        
        # 화면 출력 (2025년 기준)
        print("\n[2025년 유형별/시나리오별 CF 요약 (S1 현행, %)]")
        print(results_s1_rate[2025].round(2))

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    export_grouped_cf_full_scenarios()

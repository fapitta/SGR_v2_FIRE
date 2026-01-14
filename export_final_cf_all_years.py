import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator, MeiCalculator

def export_final_cf_full_report():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    OUTPUT_FILE_PATH = 'h:/병원환산지수연구_2027년/SGR_CF_최종_전연도_분석표.xlsx'
    YEAR_RANGE = range(2020, 2028)
    
    try:
        processor = DataProcessor(EXCEL_FILE_PATH)
        data = processor.data
        hospital_types = processor.HOSPITAL_TYPES
        sgr_calc = SgrCalculator(data, hospital_types)
        mei_calc = MeiCalculator(data, hospital_types)
        df_rel_value = data['df_rel_value']
        
        final_results = {}

        print("--- 🚀 2020-2027 환산지수 조정률(CF) 연도별 계산 시작 ---")
        for target_year in YEAR_RANGE:
            # 1. MEI 지수
            df_mei_idx = mei_calc.calc_mei_index_by_year(target_year)
            if df_mei_idx is None:
                continue

            # 2. UAF 산출
            uaf_s1 = sgr_calc.calc_paf_s1(target_year)
            uaf_s2 = sgr_calc.calc_paf_s2(target_year)
            
            # 3. 상대가치 변화지수
            try:
                # 종별 매칭을 위해 reindex 사용 (길이 불일치 방지)
                rv_idx = df_rel_value.loc[target_year - 1].reindex(hospital_types).fillna(1.0)
            except KeyError:
                rv_idx = pd.Series(1.0, index=hospital_types)
            
            # 4. CF 계산
            cf_s1_idx = df_mei_idx.multiply(1 + uaf_s1, axis=0)
            base_s2_idx = df_mei_idx.multiply(1 + uaf_s2, axis=0)
            cf_s2_idx = base_s2_idx.sub(rv_idx - 1, axis=0)
            
            final_results[target_year] = {
                'S1_Index': cf_s1_idx,
                'S1_Rate': (cf_s1_idx - 1) * 100,
                'S2_Index': cf_s2_idx,
                'S2_Rate': (cf_s2_idx - 1) * 100,
                'UAF': pd.DataFrame({'S1': uaf_s1, 'S2': uaf_s2}, index=hospital_types) * 100,
                'RV_idx': rv_idx
            }

        if not final_results:
            print("❌ 오류: 산출된 결과가 없습니다.")
            return

        with pd.ExcelWriter(OUTPUT_FILE_PATH, engine='openpyxl') as writer:
            # 1. 전연도 요약 시트
            summary_list = []
            for y, res in final_results.items():
                s1_avg = res['S1_Rate']['평균']
                s2_avg = res['S2_Rate']['평균']
                rv_rate = (res['RV_idx'] - 1) * 100
                
                # 모든 Series가 hospital_types 인덱스로 정렬되어 있음
                df_y = pd.DataFrame({
                    '연도': y,
                    '종별': hospital_types,
                    '현행_S1_조정률(%)': s1_avg.values,
                    '개선_S2_조정률(%)': s2_avg.values,
                    '현행_S1_인덱스': res['S1_Index']['평균'].values,
                    '개선_S2_인덱스': res['S2_Index']['평균'].values,
                    '상대가치차감율(%)': rv_rate.values,
                    'UAF_S1(%)': res['UAF']['S1'].values,
                    'UAF_S2(%)': res['UAF']['S2'].values
                })
                summary_list.append(df_y)
            
            pd.concat(summary_list).to_excel(writer, sheet_name='전연도_평균_요약', index=False)

            # 2. 모형별 추이 (평균 시나리오 기준)
            for model_name in ['S1', 'S2']:
                for mode in ['Rate', 'Index']:
                    combined = pd.DataFrame(index=hospital_types)
                    for y in YEAR_RANGE:
                        if y in final_results:
                            combined[f"{y}년"] = final_results[y][f'{model_name}_{mode}']['평균']
                    combined.to_excel(writer, sheet_name=f'{model_name}_{mode}_추이')

            # 3. 2025년 상세 (16개 시나리오)
            if 2025 in final_results:
                r25 = final_results[2025]
                r25['S1_Rate'].to_excel(writer, sheet_name='2025_S1_조정률(%)')
                r25['S1_Index'].to_excel(writer, sheet_name='2025_S1_지수')
                r25['S2_Rate'].to_excel(writer, sheet_name='2025_S2_조정률(%)')
                r25['S2_Index'].to_excel(writer, sheet_name='2025_S2_지수')

        print(f"\n✅ 리포트 생성 완료: {OUTPUT_FILE_PATH}")
        print("\n[검산: 2025년 상급종합병원 평균 시나리오]")
        v = final_results[2025]
        print(f" - S1 (현행): 지수 {v['S1_Index'].loc['상급종합', '평균']:.4f} / 조정률 {v['S1_Rate'].loc['상급종합', '평균']:.2f}%")
        print(f" - S2 (개선): 지수 {v['S2_Index'].loc['상급종합', '평균']:.4f} / 조정률 {v['S2_Rate'].loc['상급종합', '평균']:.2f}%")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    export_final_cf_full_report()

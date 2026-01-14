import pandas as pd
import numpy as np
import io
from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator, FinalRateCalculator, MeiCalculator

def export_macro_history_report():
    print("--- 거시지표 모형 전연도(2020-2027) 리포트 생성 시작 ---")
    
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    processor = DataProcessor(EXCEL_FILE_PATH)
    data = processor.data
    hospital_types = processor.HOSPITAL_TYPES
    group_mapping = processor.GROUP_MAPPING
    
    sgr_calc = SgrCalculator(data, hospital_types)
    mei_calc = MeiCalculator(data, hospital_types)
    final_calc = FinalRateCalculator(data, group_mapping)
    
    years = range(2020, 2028)
    
    # 결과를 담을 딕셔너리 (Key: 모형이름, Value: {Year: DataFrame})
    results_10 = {
        '실질 GDP 모형': pd.DataFrame(index=hospital_types),
        'MEI 모형': pd.DataFrame(index=hospital_types),
        '거시지표 연계 모형': pd.DataFrame(index=hospital_types)
    }
    
    results_group = {
        '실질 GDP 모형': pd.DataFrame(index=list(group_mapping.keys())),
        'MEI 모형': pd.DataFrame(index=list(group_mapping.keys())),
        '거시지표 연계 모형': pd.DataFrame(index=list(group_mapping.keys()))
    }
    
    for y in years:
        # MEI (T-2 기준)
        df_mei = mei_calc.calc_mei_index_by_year(y)
        if df_mei is None:
            print(f"   ⚠️ {y}년 MEI 데이터 부족 (건너뜀)")
            continue
            
        # 거시지표 구성요소 (T-2 기준)
        comp_macro = sgr_calc._calc_sgr_components(y - 2)
        if comp_macro is None:
            print(f"   ⚠️ {y}년 거시지표 데이터 부족 (건너뜀)")
            continue
            
        # 모형 산출
        df_10, df_group = final_calc.calc_macro_final_rate(df_mei, comp_macro, y)
        
        # %로 변환하여 저장
        for model_name in results_10.keys():
            results_10[model_name][f"{y}년"] = ((df_10[model_name] - 1) * 100).round(2)
            results_group[model_name][f"{y}년"] = ((df_group[model_name] - 1) * 100).round(2)

    # 엑셀 저장
    output_path = 'h:/병원환산지수연구_2027년/거시지표모형_전연도_분석표.xlsx'
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        for model_name in results_10.keys():
            # 시트명 제한 (31자) 해결
            sheet_name_10 = f"{model_name[:10]}_10종"
            sheet_name_group = f"{model_name[:10]}_5그룹"
            
            results_10[model_name].to_excel(writer, sheet_name=sheet_name_10)
            results_group[model_name].to_excel(writer, sheet_name=sheet_name_group)
            
        # 통합 요약 시트 (종합 비교용)
        # 2025년 기준 5그룹 종합 비교
        if '2025년' in results_group['실질 GDP 모형'].columns:
            summary_2025 = pd.DataFrame({
                '실질 GDP 모형': results_group['실질 GDP 모형']['2025년'],
                'MEI 모형': results_group['MEI 모형']['2025년'],
                '거시지표 연계 모형': results_group['거시지표 연계 모형']['2025년']
            })
            summary_2025.to_excel(writer, sheet_name='2025년_모형별_비교')

    print(f"✅ 리포트 생성 완료: {output_path}")

if __name__ == "__main__":
    export_macro_history_report()

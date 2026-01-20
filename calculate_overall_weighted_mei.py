import pandas as pd
import numpy as np
import warnings
from 파이썬용_sgr_2027 import DataProcessor, MeiCalculator

# 경고 무시
warnings.filterwarnings('ignore')

def calculate_overall_weighted_mei_full_range(file_path):
    # 1. 데이터 로드 및 초기화
    processor = DataProcessor(file_path)
    hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    mei_calc = MeiCalculator(processor.raw_data, hospital_types)
    
    # 진료비 데이터 가져오기
    df_exp = processor.raw_data['df_expenditure']
    
    # 2. 가능한 모든 연도 탐색 (2010 ~ 2028)
    # factor_pd가 2010년부터 있으므로, target_year는 2012년부터 가능성 있음
    years = sorted(df_exp.index.unique())
    results = []
    
    print(f"탐색 연도 범위: {min(years)} - {max(years)}")
    
    for year in years:
        try:
            # 해당 연도의 종별 MEI 평균 (지수 형태)
            df_mei = mei_calc.calc_mei_index_by_year(year)
            
            # 산출이 안 되는 경우 (데이터 부족 등) 스킵
            if df_mei is None or '평균' not in df_mei.columns:
                continue
                
            mei_averages = df_mei['평균'] # Series (indexed by hospital_types)
            
            # 해당 연도의 실제 진료비 가중치
            if year in df_exp.index:
                exp_year = df_exp.loc[year, hospital_types].fillna(0)
                total_exp = exp_year.sum()
                
                if total_exp > 0:
                    # 가중평균 MEI = Σ(종별 MEI평균 * 종별 진료비) / Σ(진료비)
                    weighted_mei = (mei_averages * exp_year).sum() / total_exp
                    
                    results.append({
                        '연도': int(year),
                        '전체가중평균_MEI': round(weighted_mei, 6),
                        '총진료비': round(total_exp, 2)
                    })
        except Exception as e:
            # 특정 연도 산출 실패 시 로그 남기고 계속 진행
            print(f"[정보] {year}년 MEI 산출 불가: {e}")
            continue
    
    # 3. 결과 저장 및 출력
    result_df = pd.DataFrame(results)
    output_file = '연도별_전체_가중평균_MEI_결과_최대범위.xlsx'
    result_df.to_excel(output_file, index=False)
    
    print("\n### [연도별 전체 가중평균 MEI (최대 데이터 확보 범위)] ###")
    print(result_df)
    print(f"\n파일이 '{output_file}'로 저장되었습니다.")

if __name__ == "__main__":
    calculate_overall_weighted_mei_full_range('SGR_data.xlsx')

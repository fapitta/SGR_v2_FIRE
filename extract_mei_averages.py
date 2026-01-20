import pandas as pd
import numpy as np
import warnings
from 파이썬용_sgr_2027 import DataProcessor, MeiCalculator

# 경고 무시
warnings.filterwarnings('ignore')

def extract_mei_averages(file_path):
    # 1. 데이터 로드
    processor = DataProcessor(file_path)
    hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    mei_calc = MeiCalculator(processor.raw_data, hospital_types)
    
    # 2. 연도별 MEI 평균 산출 (2014 ~ 2028)
    years = range(2014, 2029)
    results = {}
    
    for year in years:
        df_mei = mei_calc.calc_mei_index_by_year(year)
        if df_mei is not None and '평균' in df_mei.columns:
            # '평균' 컬럼만 추출하여 연도별로 저장
            results[year] = df_mei['평균'].round(6)
            
    # 3. 데이터프레임 변환
    mei_avg_df = pd.DataFrame(results).T
    mei_avg_df.index.name = '연도'
    
    # 엑셀 저장
    output_file = '연도별_종별_MEI_평균_결과.xlsx'
    mei_avg_df.to_excel(output_file)
    
    print("\n### [연도별 종별 MEI 평균 (mei_평균) 지수] ###")
    print(mei_avg_df)
    print(f"\n파일이 '{output_file}'로 저장되었습니다.")

if __name__ == "__main__":
    extract_mei_averages('SGR_data.xlsx')

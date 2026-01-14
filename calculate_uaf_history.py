import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings('ignore')

from 파이썬용_sgr_2027 import DataProcessor, SgrCalculator

def calculate_uaf_history():
    EXCEL_FILE_PATH = 'h:/병원환산지수연구_2027년/파이썬_SGR_데이터SET.xlsx'
    # 구하고자 하는 환산지수 타겟 연도: 2020-2027
    TARGET_YEARS = range(2020, 2028)
    
    processor = DataProcessor(EXCEL_FILE_PATH)
    data = processor.data
    hospital_types = processor.HOSPITAL_TYPES
    sgr_calc = SgrCalculator(data, hospital_types)
    
    ae_actual = data['df_expenditure']
    
    # 먼저 사전 계산: 모든 가능 연도의 TGE_S1, TGE_S2, SGR_S1, SGR_S2
    # 최대 과거 2009년(UAF_2020의 누적 시작)부터 2026년까지
    ALL_CALC_YEARS = range(2009, 2028)
    tge_s1_dict = {}
    tge_s2_dict = {}
    sgr_idx_s1_dict = {}
    sgr_idx_s2_dict = {}
    
    for y in ALL_CALC_YEARS:
        comp = sgr_calc._calc_sgr_components(y)
        if comp:
            s1_idx = sgr_calc.calc_sgr_index(comp, model='S1')
            s2_idx = sgr_calc.calc_sgr_index(comp, model='S2')
            sgr_idx_s1_dict[y] = s1_idx
            sgr_idx_s2_dict[y] = s2_idx
            
            if (y-1) in ae_actual.index:
                tge_s1_dict[y] = ae_actual.loc[y-1] * s1_idx
                tge_s2_dict[y] = ae_actual.loc[y-1] * s2_idx
            else:
                tge_s1_dict[y] = pd.Series(np.nan, index=hospital_types)
                tge_s2_dict[y] = pd.Series(np.nan, index=hospital_types)
        else:
            sgr_idx_s1_dict[y] = pd.Series(np.nan, index=hospital_types)
            sgr_idx_s2_dict[y] = pd.Series(np.nan, index=hospital_types)
            tge_s1_dict[y] = pd.Series(np.nan, index=hospital_types)
            tge_s2_dict[y] = pd.Series(np.nan, index=hospital_types)

    uaf_s1_final = {}
    uaf_s2_final = {}

    for T in TARGET_YEARS:
        # --- [S1] 현행 모형 산출 ---
        # T-2년 최신자료
        y_recent = T - 2
        
        # 1. 단기분 (y_recent)
        if y_recent in tge_s1_dict and y_recent in ae_actual.index:
            gap_short = (tge_s1_dict[y_recent] - ae_actual.loc[y_recent]) / ae_actual.loc[y_recent]
        else:
            gap_short = pd.Series(np.nan, index=hospital_types)
            
        # 2. 누적분 (T-11 ~ T-2 : 10개년)
        y_start = T - 11
        y_end = T - 2
        
        sum_tge = pd.Series(0.0, index=hospital_types)
        sum_ae = pd.Series(0.0, index=hospital_types)
        count = 0
        for y in range(y_start, y_end + 1):
            if y in tge_s1_dict and y in ae_actual.index:
                sum_tge += tge_s1_dict[y]
                sum_ae += ae_actual.loc[y]
                count += 1
        
        if count > 0 and (T-2) in ae_actual.index and (T-1) in sgr_idx_s1_dict:
            # 이미지 공식: (Sum(TGE)-Sum(AE)) / (AE_{T-2} * (1+SGR_{T-1}))
            # 주의: sgr_idx는 이미 (1+r) 형태임
            denom = ae_actual.loc[T-2] * sgr_idx_s1_dict[T-1]
            gap_accum = (sum_tge - sum_ae) / denom
        else:
            gap_accum = pd.Series(np.nan, index=hospital_types)
            
        # 최종 S1 PAF = 단기*0.75 + 누적*0.33 (이미지 수치)
        uaf_s1_val = (gap_short * 0.75) + (gap_accum * 0.33)
        uaf_s1_final[f"UAF_{T}"] = uaf_s1_val

        # --- [S2] 개선 모형 산출 ---
        # 이미지 2 공식: 0.5*Gap(T-2) + 0.3*Gap(T-3) + 0.2*Gap(T-4)
        gaps_s2 = []
        for lag in [2, 3, 4]:
            y_lag = T - lag
            if y_lag in tge_s2_dict and y_lag in ae_actual.index:
                gap = (tge_s2_dict[y_lag] - ae_actual.loc[y_lag]) / ae_actual.loc[y_lag]
                gaps_s2.append(gap)
            else:
                gaps_s2.append(pd.Series(np.nan, index=hospital_types))
        
        uaf_s2_val = (gaps_s2[0] * 0.5) + (gaps_s2[1] * 0.3) + (gaps_s2[2] * 0.2)
        uaf_s2_final[f"UAF_{T}"] = uaf_s2_val

    # 결과 정리
    df_uaf_s1 = pd.DataFrame(uaf_s1_final).T * 100 # % 단위
    df_uaf_s2 = pd.DataFrame(uaf_s2_final).T * 100 # % 단위
    
    print("\n=== [S1] 현행 모형 UAF 결과 (% 단위, 2020-2027) ===")
    print(df_uaf_s1.round(2))
    
    print("\n=== [S2] 개선 모형 UAF 결과 (% 단위, 2020-2027) ===")
    print(df_uaf_s2.round(2))

    # 엑셀 저장
    with pd.ExcelWriter('h:/병원환산지수연구_2027년/UAF_산출_최종결과.xlsx') as writer:
        df_uaf_s1.to_excel(writer, sheet_name='UAF_S1_현행')
        df_uaf_s2.to_excel(writer, sheet_name='UAF_S2_개선')
    print(f"\n✅ UAF 산출 결과가 'UAF_산출_최종결과.xlsx'로 저장되었습니다.")

if __name__ == "__main__":
    calculate_uaf_history()

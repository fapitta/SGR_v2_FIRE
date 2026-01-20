import pandas as pd
import numpy as np

def calculate_weighted_average_cf(file_path):
    # Load data
    df_exp = pd.read_excel(file_path, sheet_name='expenditure_real')
    df_cf = pd.read_excel(file_path, sheet_name='cf_t')
    
    # 10 Hospital Types
    hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    
    # Clean indices
    df_exp = df_exp.set_index('연도')
    df_cf = df_cf.set_index('연도')
    
    # Ensure they are numeric
    df_exp = df_exp[hospital_types].apply(pd.to_numeric, errors='coerce')
    df_cf = df_cf[hospital_types].apply(pd.to_numeric, errors='coerce')
    
    # Find common years
    common_years = df_exp.index.intersection(df_cf.index).sort_values()
    
    results = []
    
    for year in common_years:
        exp_year = df_exp.loc[year]
        cf_year = df_cf.loc[year]
        
        # Calculate Total Expenditure for the year
        total_exp = exp_year.sum()
        
        if total_exp > 0:
            # Weighted sum: Sum(CF * Expenditure)
            weighted_sum = (cf_year * exp_year).sum()
            weighted_avg_cf = weighted_sum / total_exp
            
            results.append({
                '연도': int(year),
                '가중평균환산지수': round(weighted_avg_cf, 4),
                '총진료비': round(total_exp, 2)
            })
    
    result_df = pd.DataFrame(results)
    output_file = '가중평균환산지수_계산결과.xlsx'
    result_df.to_excel(output_file, index=False)
    print(f"Calculation complete. Saved to {output_file}")
    print(result_df)

if __name__ == "__main__":
    calculate_weighted_average_cf('SGR_data.xlsx')

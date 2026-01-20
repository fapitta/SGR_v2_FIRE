import pandas as pd
import numpy as np
import os

def calculate_weighted_average_law(file_path):
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Load data
    try:
        df_exp = pd.read_excel(file_path, sheet_name='expenditure_real')
        df_law = pd.read_excel(file_path, sheet_name='law')
    except Exception as e:
        print(f"Error loading Excel sheets: {e}")
        return
    
    # 10 Hospital Types
    hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
    
    # Set '연도' as index
    if '연도' in df_exp.columns:
        df_exp = df_exp.set_index('연도')
    elif 'Year' in df_exp.columns:
        df_exp = df_exp.set_index('Year')
    else:
        df_exp = df_exp.set_index(df_exp.columns[0])

    if '연도' in df_law.columns:
        df_law = df_law.set_index('연도')
    elif 'Year' in df_law.columns:
        df_law = df_law.set_index('Year')
    else:
        df_law = df_law.set_index(df_law.columns[0])
    
    # Clean index: convert to numeric and drop NaNs
    df_exp.index = pd.to_numeric(df_exp.index, errors='coerce')
    df_exp = df_exp[df_exp.index.notna()].astype(int)
    
    df_law.index = pd.to_numeric(df_law.index, errors='coerce')
    df_law = df_law[df_law.index.notna()].astype(int)

    # Ensure all hospital types are present in both dataframes
    available_exp_types = [t for t in hospital_types if t in df_exp.columns]
    available_law_types = [t for t in hospital_types if t in df_law.columns]
    common_types = list(set(available_exp_types) & set(available_law_types))
    
    print(f"Common hospital types found: {common_types}")
    
    # Ensure they are numeric
    df_exp = df_exp[common_types].apply(pd.to_numeric, errors='coerce').fillna(0)
    df_law = df_law[common_types].apply(pd.to_numeric, errors='coerce').fillna(0)
    
    # Find common years
    common_years = df_exp.index.intersection(df_law.index).sort_values()
    
    results = []
    
    for year in common_years:
        exp_year = df_exp.loc[year]
        law_year = df_law.loc[year]
        
        # Calculate Total Expenditure for the search year
        total_exp = exp_year.sum()
        
        if total_exp > 0:
            # Weighted sum: Sum(Law_Index * Expenditure)
            weighted_sum = (law_year * exp_year).sum()
            weighted_avg_law = weighted_sum / total_exp
            
            results.append({
                '연도': int(year),
                '전체_가중평균_법과제도지수': round(weighted_avg_law, 4),
                '총진료비': round(total_exp, 2)
            })
    
    if results:
        result_df = pd.DataFrame(results)
        output_file = '전체_가중평균_법과제도지수_결과.xlsx'
        result_df.to_excel(output_file, index=False)
        print(f"Calculation complete. Saved to {output_file}")
        print(result_df)
    else:
        print("No calculation results produced. Please check common years and types.")

if __name__ == "__main__":
    calculate_weighted_average_law('SGR_data.xlsx')

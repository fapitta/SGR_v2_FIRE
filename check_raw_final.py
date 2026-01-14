import pandas as pd
file = 'SGR_data.xlsx'
target_year = 2023
xl = pd.ExcelFile(file)
# Mapping internal names back to sheet names to be sure
sheet_map = {
    'df_expenditure': 'expenditure_real',
    'df_weights': 'cost_structure',
    'df_raw_mei_inf': 'factor_pd',
    'df_gdp': 'GDP',
    'df_pop': 'pop',
    'df_sgr_reval': 'cf_t',
    'df_sgr_law': 'law',
    'df_rel_value': 'rvs'
}

for internal, name in sheet_map.items():
    if name in xl.sheet_names:
        df = pd.read_excel(file, sheet_name=name)
        # Handle years
        if internal != 'df_weights':
            col = '연도' if '연도' in df.columns else df.columns[0]
            row = df[df[col] == target_year]
            print(f"\n--- Sheet: {name} (Year {target_year}) ---")
            print(row)
        else:
            print(f"\n--- Sheet: {name} ---")
            print(df.head())

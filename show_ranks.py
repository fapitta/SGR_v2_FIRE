
import pandas as pd
import numpy as np
from 파이썬용_sgr_2027 import run_sgr_analysis_for_web

target_year = 2025
analysis_result = run_sgr_analysis_for_web(target_year)
results = analysis_result['results']

# Convert results into a DataFrame for easier ranking
df = pd.DataFrame(results)

# Clean up values (remove 'N/A' or convert to float)
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# Calculate Ranks for each model (columns)
# rank(ascending=False, method='min') gives 1 for highest
df_ranks = df.rank(ascending=False, method='min', axis=0).astype(int)

# Create a combined display (Value and Rank)
final_display = pd.DataFrame(index=df.index)
for col in df.columns:
    final_display[f'{col} (%)'] = df[col]
    final_display[f'{col} (순위)'] = df_ranks[col]

print("--- 2025년도 분석 결과 및 순위 ---")
print(final_display.T)

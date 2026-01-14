
import pandas as pd
import numpy as np
import os

file_path = 'SGR_data.xlsx'

def load_sheet(name):
    df = pd.read_excel(file_path, sheet_name=name, index_col=None)
    if not df.empty and len(df.columns) > 0:
        df = df.set_index(df.columns[0])
    
    # Cleaning as in the main script
    df.columns = [str(c).strip() for c in df.columns]
    if df.index.dtype == 'object':
        df.index = [str(i).strip() if isinstance(i, str) else i for i in df.index]
    return df

df_weights_raw = load_sheet('cost_structure')
df_weights = df_weights_raw.T

print("--- DataProcessor cleaned df_weights index ---")
for i in df_weights.index:
    print(f"'{i}' : {[hex(ord(c)) for c in i]}")

hospital_types = ['상급종합', '종합병원', '병원', '요양병원', '의원', '치과병원', '치과의원', '한방병원', '한의원', '약국']
print("\n--- Canonical hospital_types ---")
for i in hospital_types:
    print(f"'{i}' : {[hex(ord(c)) for c in i]}")

print("\n--- Reindex Result ---")
reindexed = df_weights['인건비'].reindex(hospital_types)
print(reindexed)

print("\n--- Check for 0.0 values in MEI output ---")
# Simulating the calc
res = (df_weights['인건비'].reindex(hospital_types).fillna(0) * 1.04)
print(res)

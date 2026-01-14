import pandas as pd
from 파이썬용_sgr_2027 import processor

def test_original_data():
    years = [2020, 2021, 2022, 2023, 2024, 2025]
    
    # MEI 데이터
    mei_data = {}
    df_mei = processor.raw_data['df_raw_mei_inf']
    print("df_mei columns:", df_mei.columns.tolist())
    print("df_mei index type:", type(df_mei.index[0]))
    
    fields = ['인건비_1', '인건비_2', '인건비_3', '관리비_1', '관리비_2', '재료비_1', '재료비_2']
    for field in fields:
        mei_data[field] = {}
        for year in years:
            if year in df_mei.index and field in df_mei.columns:
                val = df_mei.loc[year, field]
                mei_data[field][str(year)] = float(val) if pd.notna(val) else None
            else:
                mei_data[field][str(year)] = f"MISSING (y:{year in df_mei.index}, f:{field in df_mei.columns})"
    
    import json
    print(json.dumps(mei_data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test_original_data()

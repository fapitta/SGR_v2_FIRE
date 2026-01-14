from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine
import pandas as pd

def get_new_breakdown():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    engine = CalculationEngine(processor.raw_data)
    history, details, bulk = engine.run_full_analysis(2025)
    
    y = 2025
    uaf_s1 = history['UAF_S1'][y]
    s1_adj = history['S1'][y]
    
    print(f"=== [Breakdown for 2025 SGR(S1)] ===")
    for key in ['치과병원', '치과의원', '치과(계)', '한방병원', '한의원', '한방(계)']:
        u = uaf_s1.get(key, 0)
        adj = s1_adj.get(key, 0)
        print(f"[{key}] UAF: {u}% / Final Adj: {adj}%")

    # Deep dive into aggregated UAF for 치과(계)
    # AE 2023 for weights
    ae_2023 = processor.raw_data['df_expenditure'].loc[2023]
    hsp = '치과병원'
    cln = '치과의원'
    
    u_h = uaf_s1[hsp]
    u_c = uaf_s1[cln]
    w_h = ae_2023[hsp] / (ae_2023[hsp] + ae_2023[cln])
    w_c = 1 - w_h
    
    print(f"\nGroup Weighted Average Check for 치과(계):")
    print(f"  - ({u_h}% * {w_h:.4f}) + ({u_c}% * {w_c:.4f}) = {u_h*w_h + u_c*w_c:.2f}%")
    print(f"  - My App Value: {uaf_s1['치과(계)']}%")

if __name__ == "__main__":
    get_new_breakdown()

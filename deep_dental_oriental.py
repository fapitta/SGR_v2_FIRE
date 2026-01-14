from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine
import pandas as pd
import numpy as np

def deep_inspect_dental_oriental():
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    engine = CalculationEngine(processor.raw_data)
    data = processor.raw_data
    
    types = ['치과병원', '치과의원', '한방병원', '한의원']
    groups = {
        '치과(계)': ['치과병원', '치과의원'],
        '한방(계)': ['한방병원', '한의원']
    }
    
    print("=== [1] Data Availability Check (2014-2023) ===")
    exp = data['df_expenditure']
    law = data['df_sgr_law']
    reval = data['df_sgr_reval']
    
    for t in types:
        print(f"\n[{t}]")
        avg_exp = exp[t].mean() if t in exp.columns else 0
        has_law = t in law.columns
        has_reval = t in reval.columns
        print(f"  - Avg Expenditure: {avg_exp:,.2f} / Has Law: {has_law} / Has Reval: {has_reval}")
        if has_law: print(f"  - Law Samples (2020-2023): {law[t].loc[2020:2023].tolist()}")
        if has_reval: print(f"  - Reval Samples (2020-2023): {reval[t].loc[2020:2023].tolist()}")

    print("\n=== [2] Weighting Logic Check (2023 weights) ===")
    ae_2023 = exp.loc[2023]
    for g, members in groups.items():
        sub = ae_2023[members]
        total = sub.sum()
        print(f"[{g}] Weights (AE 2023):")
        for m in members:
            w = sub[m] / total
            print(f"  - {m}: {sub[m]:,.2f} ({w:.2%})")

    print("\n=== [3] MEI 2025 Component Weights ===")
    w_mei = data['df_weights']
    print(w_mei.loc[types])

    print("\n=== [4] Calculating UAF 2025 S1 Detailed ===")
    # Recalculate with corrected denom (1 + idx) 
    # and print intermediate results for comparison
    uaf_results = engine.sgr_calc.calc_paf_s1(2025)
    
    print("\n[UAF S1 Result Summary]")
    for t in types:
        print(f"  - {t}: {uaf_results[t]*100:.2f}%")
        
    for g, members in groups.items():
        w = ae_2023[members] / ae_2023[members].sum()
        g_uaf = (uaf_results[members] * w).sum()
        print(f"  - {g}: {g_uaf*100:.2f}% (Calculated via AE weights)")

if __name__ == "__main__":
    deep_inspect_dental_oriental()

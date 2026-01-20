
import sys
import os
import pandas as pd

# Add current directory to path
sys.path.append(os.getcwd())

from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine

def verify_budget_analysis():
    print("Loading data...")
    processor = DataProcessor('SGR_data.xlsx')
    engine = CalculationEngine(processor.raw_data)
    
    print("Running full analysis...")
    history, components, bulk_sgr = engine.run_full_analysis(target_year=2025)
    
    print("\nVerifying Budget Analysis for 2025...")
    if 2025 not in bulk_sgr['budget_analysis']:
        print("FAIL: 2025 not in budget_analysis")
        return
    
    b_data = bulk_sgr['budget_analysis'][2025]
    
    # Check keys
    required_keys = ['Macro', 'S1', 'S2']
    missing_keys = [k for k in required_keys if k not in b_data]
    
    if missing_keys:
        print(f"FAIL: Missing keys in budget_analysis[2025]: {missing_keys}")
    else:
        print("SUCCESS: usage_analysis keys 'Macro', 'S1', 'S2' found.")
        
    # Check content of Macro
    if 'GDP' in b_data['Macro']:
        print(f"  Macro/GDP Rate (Total): {b_data['Macro']['GDP']['rate'].get('전체')}")
        print(f"  Macro/GDP Budget (Total): {b_data['Macro']['GDP']['budget'].get('전체')}")
    else:
        print("FAIL: Macro/GDP missing")

    # Check content of S2
    if 'AR_Average' in b_data['S2']:
         print(f"  S2/AR_Average Rate (Total): {b_data['S2']['AR_Average']['rate'].get('전체')}")
         print(f"  S2/AR_Average Budget (Total): {b_data['S2']['AR_Average']['budget'].get('전체')}")
    else:
         print("WARN: S2/AR_Average missing (might be expected if AR calc failed)")

if __name__ == "__main__":
    verify_budget_analysis()

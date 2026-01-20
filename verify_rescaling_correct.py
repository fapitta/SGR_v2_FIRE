
import sys
import pandas as pd
import numpy as np

# Adjust path to import from the main app file
sys.path.append('h:/병원환산지수연구_2027년/SGR앱개발_v2')

try:
    # Proper import
    from 파이썬용_sgr_2027 import CalculationEngine, DataProcessor

    print("Loading data...")
    processor = DataProcessor('SGR_data.xlsx')
    
    # CORRECT Initialization: PASS raw_data dict, not processor object
    engine = CalculationEngine(processor.raw_data)

    print("Running analysis for 2025...")
    history, details, bulk_sgr = engine.run_full_analysis(2025)

    print("\n--- FINAL VERIFICATION ---")
    
    # 1. Check if S1_Rescaled exists and has data
    if 'S1_Rescaled' in history and 2025 in history['S1_Rescaled']:
        rescaled_data = history['S1_Rescaled'][2025]
        print(f"[SUCCESS] S1_Rescaled (2025) Data: {rescaled_data}")
        
        # Check if values are different from S1 (proof of rescaling)
        s1_data = history['S1'][2025]
        print(f"[INFO] Original S1 (2025) Data: {s1_data}")
        
        if rescaled_data['전체'] != s1_data['전체']:
             print(f"[SUCCESS] Rescaling applied! ({s1_data['전체']} -> {rescaled_data['전체']})")
        else:
             print("[WARN] Values are identical. Check if Contract Rate equals Standard Rate or if Data is missing.")
             
    else:
        print("[FAIL] S1_Rescaled (2025) Key MISSING or Empty")

    # 2. Check Budget Constraints (User reported this empty)
    # Note: 'budget_constraints' is populated in bulk_sgr['budget_constraints'] if logic is reached
    if 'budget_constraints' in bulk_sgr and bulk_sgr['budget_constraints']:
        print("[SUCCESS] Budget Constraints Data Found")
        # print sample key
        print(f"Keys: {list(bulk_sgr['budget_constraints'].keys())}")
    else:
        # If empty, check if it's because loop didn't reach it (unlikely now) or df_contract is empty
        print("[FAIL] Budget Constraints Dictionary is EMPTY.")
        print("Debugging Contract Data...")
        if 'df_contract' in processor.raw_data:
             df_c = processor.raw_data['df_contract']
             print(f"Contract Data Head:\n{df_c.head()}")
             if 2024 in df_c.index:
                 print(f"2024 Data: {df_c.loc[2024]}")
             else:
                 print("2024 Data NOT found in Contract Data.")
        else:
             print("df_contract NOT found in raw_data")

except Exception as e:
    print(f"\n[CRITICAL ERROR] Execution Failed: {e}")
    import traceback
    traceback.print_exc()

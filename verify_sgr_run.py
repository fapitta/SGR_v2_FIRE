
import sys
import pandas as pd
# Adjust path to import from the main app file
sys.path.append('h:/병원환산지수연구_2027년/SGR앱개발_v2')

try:
    from 파이썬용_sgr_2027 import CalculationEngine, DataProcessor

    print("Loading data...")
    processor = DataProcessor('SGR_data.xlsx')
    engine = CalculationEngine(processor)

    print("Running analysis for 2025...")
    history, details, bulk_sgr = engine.run_full_analysis(2025)

    print("\n--- Verification Results ---")
    
    # Check S1, S2 (Pure Results)
    if 'S1' in history and 2025 in history['S1']:
        print("[OK] S1 (2025) Data Found:", history['S1'][2025])
    else:
        print("[FAIL] S1 (2025) Data MISSING")

    if 'S2' in history and 2025 in history['S2']:
        print("[OK] S2 (2025) Data Found:", history['S2'][2025])
    else:
        print("[FAIL] S2 (2025) Data MISSING")
    
    # Check Budget Constraints (The new part)
    if 'budget_constraints' in bulk_sgr:
        print("[OK] Budget Constraints Found")
        print(bulk_sgr['budget_constraints'])
    else:
        print("[FAIL] Budget Constraints MISSING (This is the specific issue reported)")

    # Check Rescaled Keys
    if 'S1_Rescaled' in history:
         print("[OK] S1_Rescaled Key Exists")
    else:
         print("[FAIL] S1_Rescaled Key MISSING")

except Exception as e:
    print(f"\n[CRITICAL ERROR] Execution Failed: {e}")
    import traceback
    traceback.print_exc()

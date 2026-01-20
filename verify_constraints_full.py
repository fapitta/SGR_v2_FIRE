
import sys
import os
import pandas as pd

sys.path.append(os.getcwd())
from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine

def verify_constraints_logic():
    print("Loading data...")
    processor = DataProcessor('SGR_data.xlsx')
    engine = CalculationEngine(processor.raw_data)
    
    print("Running full analysis (Target 2025)...")
    history, components, bulk_sgr = engine.run_full_analysis(target_year=2025)
    
    print("\nVerifying Budget Constraints for 2025...")
    if 'budget_constraints' not in bulk_sgr:
        print("FAIL: budget_constraints key missing")
        return

    c_data = bulk_sgr['budget_constraints']
    
    scenarios = ['S1_1', 'S1_2', 'S2_1', 'S2_2', 'S2_3']
    all_present = True
    
    for s in scenarios:
        if s not in c_data:
            print(f"FAIL: Scenario {s} missing")
            all_present = False
        else:
            # Check deep structure
            # Should have Macro, S1, S2
            if 'Macro' in c_data[s] and 'S1' in c_data[s] and 'S2' in c_data[s]:
                # Check value scaling (just sanity check)
                # Compare S1_1 (Budget Growth) vs S2_3 (prev year rate) - they should be different
                val_macro = c_data[s]['Macro']['GDP']['budget'].get('전체')
                print(f"  [{s}] Macro/GDP Budget (Total): {val_macro}")
            else:
                print(f"FAIL: Scenario {s} missing deep structure (Macro/S1/S2)")
                all_present = False
    
    if all_present:
        print("SUCCESS: All 5 scenarios present with full model structure.")

if __name__ == "__main__":
    verify_constraints_logic()


import os
import sys
import json
import pandas as pd

# Import the logic from the app file
# Assuming we can import it if it's in the same dir
sys.path.append(os.getcwd())
from 파이썬용_sgr_2027 import CalculationEngine, DataProcessor

def test_forecast():
    processor = DataProcessor('SGR_data.xlsx')
    engine = CalculationEngine(processor.raw_data)
    
    # Run analysis for 2025
    history, details, bulk_sgr = engine.run_full_analysis(target_year=2025)
    
    forecast = bulk_sgr.get('financial_forecast')
    if not forecast:
        print("FAILED: No financial forecast found in bulk_sgr")
        return
        
    print("SUCCESS: Financial forecast found")
    
    for m in ['S1', 'S2']:
        print(f"\nModel: {m}")
        # Debug sum for 2024
        t2024 = history[f'Target_{m}'].get(2024, {})
        indiv_sum = sum(t2024.get(ht, 0) for ht in engine.HOSPITAL_TYPES)
        print(f"  Debug 2024 Sum: {indiv_sum:,.0f}")
        
        for year in range(2024, 2029):
            data = forecast[m].get(year)
            if data:
                print(f"  {year}: Premium={data['premium_income']:,}, Exp={data['expenditure']:,}, Net={data['net_balance']:,}, Acc={data['acc_balance']:,}, Deficit={data['is_deficit']}")
            else:
                print(f"  {year}: No data")

if __name__ == "__main__":
    test_forecast()

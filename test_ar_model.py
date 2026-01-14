import sys
import os

# Add current directory to sys.path
sys.path.append(os.getcwd())

from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine
import pandas as pd
import numpy as np

def test_ar_analysis():
    processor = DataProcessor('SGR_data.xlsx')
    engine = CalculationEngine(processor.raw_data)
    history, details, bulk_sgr = engine.run_full_analysis()
    
    if 2025 in bulk_sgr['ar_analysis']:
        ar_2025 = bulk_sgr['ar_analysis'][2025]
        print(f"Number of scenarios for 2025: {len(ar_2025)}")
        if len(ar_2025) > 0:
            first = ar_2025[0]
            print(f"First scenario: {first['base_rate']}, {first['mei_scenario']}, r={first['r']}")
            print(f"Rates for '전체': {first['rates']['전체']}")
            
            # Check if weighted average of CF_adj for this scenario was zero
            # We need to reconstruct it or trust the logic
            # Final_Rate = Base_Rate + r * (CF_S - Weighted_Avg_CF_S)
            # Weighted_Avg(Final_Rate) = Weighted_Avg(Base_Rate) + r * (Weighted_Avg(CF_S) - Weighted_Avg(CF_S))
            # Weighted_Avg(Final_Rate) = Weighted_Avg(Base_Rate)
            
            # Let's check this for the first scenario
            br_key = first['base_rate']
            base_rates = history[br_key][2025]
            
            # Weighted Avg of Final Rates
            exp_2023 = processor.raw_data['df_expenditure'].loc[2023].reindex(engine.HOSPITAL_TYPES).fillna(0)
            total_exp = exp_2023.sum()
            
            final_rates = pd.Series({t: first['rates'][t] for t in engine.HOSPITAL_TYPES})
            avg_final = (final_rates * exp_2023).sum() / total_exp
            
            base_rates_indiv = pd.Series({t: base_rates[t] for t in engine.HOSPITAL_TYPES})
            avg_base = (base_rates_indiv * exp_2023).sum() / total_exp
            
            print(f"Avg Final: {avg_final:.4f}, Avg Base: {avg_base:.4f}")
            assert abs(avg_final - avg_base) < 0.1 # Should be very close
            print("AR Model weighting logic verified!")
    else:
        print("AR analysis data not found for 2025")

if __name__ == "__main__":
    test_ar_analysis()

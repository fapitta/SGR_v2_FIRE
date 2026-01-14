
from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine
import pandas as pd
import json

processor = DataProcessor('SGR_data.xlsx')
engine = CalculationEngine(processor.raw_data)
history, components, bulk_sgr = engine.run_full_analysis(target_year=2025)

mei_2024 = components['mei_raw'][2024]
print("--- MEI 2024 Data (Scenario I1M1Z1) ---")
for t, v in mei_2024['I1M1Z1'].items():
    print(f"'{t}': {v}")

print("\n--- HEX Check for Problematic Keys in Output ---")
for k in mei_2024['I1M1Z1'].keys():
    print(f"'{k}': {[hex(ord(c)) for c in k]}")

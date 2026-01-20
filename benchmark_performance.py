import time
import sys
import os

# Import the logic from the main script
# Since the script is large, I'll just copy the necessary parts or import if possible.
# For simplicity, I'll try to import.
sys.path.append(os.getcwd())
from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine

def benchmark():
    print("Loading data...")
    start_load = time.time()
    processor = DataProcessor('SGR_data.xlsx')
    print(f"Data loading took: {time.time() - start_load:.2f}s")

    print("Running full analysis...")
    start_calc = time.time()
    engine = CalculationEngine(processor.raw_data)
    history, components, bulk_sgr = engine.run_full_analysis(target_year=2025)
    print(f"Full analysis took: {time.time() - start_calc:.2f}s")

if __name__ == "__main__":
    benchmark()

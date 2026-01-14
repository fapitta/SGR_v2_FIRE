from 파이썬용_sgr_2027 import CalculationEngine, DataProcessor
import pandas as pd

try:
    processor = DataProcessor('파이썬_SGR_데이터SET.xlsx')
    engine = CalculationEngine(processor.raw_data)
    history, components, bulk_sgr = engine.run_full_analysis(target_year=2025)
    print("Success: run_full_analysis completed.")
    
    # Simulate what's in the index route
    analysis_data = {
        'history': history,
        'components': components,
        'bulk_sgr': bulk_sgr,
        'groups': engine.HOSPITAL_TYPES + ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체'],
    }
    print("Success: analysis_data dictionary created.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

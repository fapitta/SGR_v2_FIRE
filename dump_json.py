
from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine
import json
import numpy as np

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray): return obj.tolist()
        if isinstance(obj, (np.float64, np.float32)): return float(obj)
        if isinstance(obj, (np.int64, np.int32)): return int(obj)
        return super().default(obj)

processor = DataProcessor('SGR_data.xlsx')
engine = CalculationEngine(processor.raw_data)
history, components, bulk_sgr = engine.run_full_analysis(target_year=2025)

groups_list = engine.HOSPITAL_TYPES + ['병원(계)', '의원(계)', '치과(계)', '한방(계)', '약국(계)', '전체']
scenarios_list = list(components['mei_raw'][2025].keys()) if 2025 in components['mei_raw'] else ['평균', '최대', '최소', '중위수']

analysis_data = {
    'history': history,
    'components': components,
    'bulk_sgr': bulk_sgr,
    'groups': groups_list,
    'scenarios': scenarios_list
}

# Emulate index() serialization
for k, v in analysis_data.items():
    if isinstance(v, dict):
        for sk, sv in v.items():
            if hasattr(sv, 'to_dict'):
                analysis_data[k][sk] = sv.to_dict()

# Print specific MEI 2024 scenarios
print("--- JSON KEYS for MEI 2024 Scenarios ---")
mei_2024 = analysis_data['components']['mei_raw'][2024]
for scen, data in mei_2024.items():
    print(f"Scenario: {scen}, Keys: {list(data.keys())}")
    break

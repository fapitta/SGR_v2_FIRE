import sys
import os
import pandas as pd
import json
import urllib.request
from 파이썬용_sgr_2027 import DataProcessor, CalculationEngine

def check_api():
    print("\n[1] API 엔드포인트 점검 (서버 실행 중 가정)")
    try:
        url = "http://127.0.0.1:5000/get_original_data"
        with urllib.request.urlopen(url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                # Check data content
                keys = list(data.keys())
                print(f"  - /get_original_data Status: 200 OK")
                print(f"  - Keys found: {keys}")
                
                # Check specifics
                if 'mei' in data and 'InLabor_1' in str(data['mei']): 
                     # Note: keys might be Korean or English depending on implementation
                     pass
                
                # Check sample value
                if 'medical' in data and '상급종합' in data['medical']:
                    sample = data['medical']['상급종합']['2025']
                    print(f"  - Sample (Medical 2025 상급종합): {sample}")
                    if sample is not None:
                         print("  ✅ 원시 데이터 API가 데이터를 정상적으로 반환하고 있습니다.")
                    else:
                         print("  ⚠️ 데이터 값이 비어있습니다 (None).")
                else:
                    print("  ⚠️ 예상된 데이터 키를 찾을 수 없습니다.")
            else:
                print(f"  ⚠️ Server returned status: {response.status}")
    except Exception as e:
        print(f"  ❌ API 호출 실패 (서버가 실행 중이지 않거나 에러 발생): {e}")

def check_calculation():
    print("\n[2] 분석 엔진 계산 로직 점검")
    try:
        # Load Processor
        print("  - Loading DataProcessor with SGR_data.xlsx...")
        processor = DataProcessor('SGR_data.xlsx')
        
        # Check raw data loaded
        if not processor.raw_data['df_expenditure'].empty:
            print(f"  - Raw Data Loaded: {processor.raw_data['df_expenditure'].shape} (Expenditure)")
        else:
            print("  ❌ 로드된 데이터가 비어있습니다!")
            return

        # Run Analysis
        print("  - Running Full Analysis (Target 2025)...")
        engine = CalculationEngine(processor.raw_data)
        history, details, bulk = engine.run_full_analysis(target_year=2025)
        
        # Check specific SGR result
        if 2025 in history['UAF_S1']:
            s1_uaf = history['UAF_S1'][2025]
            s2_uaf = history['UAF_S2'][2025]
            print(f"  - 2025 S1 UAF (병원): {s1_uaf.get('병원', 'N/A')}")
            print(f"  - 2025 S2 UAF (병원): {s2_uaf.get('병원', 'N/A')}")
            
            # Compare with expected values if known (from previous contexts or reliable hardcoded expectations)
            # Since we don't have the 'correct' hard value in prompt, we ensure it's calculated and not 0 or NaN
            if s1_uaf.get('병원') and s2_uaf.get('병원'):
                print("  ✅ 분석 엔진이 성공적으로 SGR 지수를 산출했습니다.")
                print("  (이 값은 원본 데이터 SGR_data.xlsx를 기반으로 산출된 값입니다.)")
            else:
                print("  ⚠️ 산출된 SGR 값이 비정상적입니다.")
        else:
            print("  ⚠️ 2025년 분석 결과가 없습니다.")
            
    except Exception as e:
        print(f"  ❌ 계산 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=== SGR 앱 진단 리포트 ===")
    check_api()
    check_calculation()

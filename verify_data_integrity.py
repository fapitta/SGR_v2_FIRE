import pandas as pd
import numpy as np

def compare_excel_data(file1, file2):
    print(f"Comparing {file1} and {file2}...")
    
    xl1 = pd.ExcelFile(file1)
    xl2 = pd.ExcelFile(file2)
    
    # 시트 매핑 (SGR_data.xlsx (영문) -> 파이썬_SGR_데이터SET.xlsx (한글))
    sheet_mapping = {
        'expenditure_real': '진료비_실제',
        'cost_structure': '종별비용구조',
        'factor_pd': '생산요소_물가',
        'GDP': '1인당GDP',
        'pop': '건보대상',
        'cf_t': '연도별환산지수',
        'law': '법과제도',
        'rvs': '상대가치변화'
    }
    
    all_match = True
    
    for eng_sheet, kor_sheet in sheet_mapping.items():
        if eng_sheet not in xl1.sheet_names:
            print(f"[MISSING] {eng_sheet} not in {file1}")
            all_match = False
            continue
        if kor_sheet not in xl2.sheet_names:
            print(f"[MISSING] {kor_sheet} not in {file2}")
            all_match = False
            continue
            
        print(f"\nChecking Sheet: {eng_sheet} vs {kor_sheet}")
        
        # Load data
        df1 = pd.read_excel(xl1, sheet_name=eng_sheet)
        df2 = pd.read_excel(xl2, sheet_name=kor_sheet)
        
        # Clean numeric data for comparison (handle float precision)
        # Convert all to numeric where possible, coercing errors
        # To compare values, we might inspect shapes first
        if df1.shape != df2.shape:
            print(f"  [FAIL] Shape Mismatch: {df1.shape} vs {df2.shape}")
            # Try to see if it's just extra empty rows/cols
            # But let's just report execution
            all_match = False
        else:
            # Compare values
            # Fill NaNs with a placeholder to compare
            df1_clean = df1.fillna(-99999)
            df2_clean = df2.fillna(-99999)
            
            # Use columns from df1 for comparison (assuming columns align by position if names diff, 
            # but usually they should have same headers if data is same)
            # Check headers
            headers_match = np.array_equal(df1.columns, df2.columns)
            if not headers_match:
                print(f"  [WARN] Headers different: {df1.columns.tolist()[:3]}... vs {df2.columns.tolist()[:3]}...")
                # Continue comparing values by position
            
            try:
                # Compare underlying numpy arrays
                vals1 = df1_clean.values
                vals2 = df2_clean.values
                
                # Check for numeric proximity instead of exact match
                # Identify numeric columns
                
                are_equal = True
                diff_count = 0
                
                rows, cols = vals1.shape
                for r in range(rows):
                    for c in range(cols):
                        v1 = vals1[r, c]
                        v2 = vals2[r, c]
                        
                        is_equal = False
                        try:
                            if isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
                                if abs(v1 - v2) < 1e-5: # Tolerance
                                    is_equal = True
                            elif str(v1) == str(v2):
                                is_equal = True
                        except:
                            if v1 == v2: is_equal = True
                            
                        if not is_equal:
                            diff_count += 1
                            if diff_count < 5:
                                print(f"    Diff at ({r},{c}): {v1} != {v2}")
                            all_match = False
                            
                if diff_count == 0:
                    print("  [OK] Data matches exactly.")
                else:
                    print(f"  [FAIL] Found {diff_count} differences.")
                    
            except Exception as e:
                print(f"  [ERROR] Comparison failed checking content: {e}")
                
    return all_match

if __name__ == "__main__":
    file_new = 'SGR_data.xlsx'
    file_old = '파이썬_SGR_데이터SET.xlsx'
    
    print("=== 원시 데이터 파일 (SGR_data.xlsx) 검증 ===")
    match = compare_excel_data(file_new, file_old)
    
    if match:
        print("\n[RESULT] 두 파일의 데이터 내용이 '완벽하게 일치'합니다.")
        print("SGR_data.xlsx를 사용하여도 분석 결과는 동일할 것입니다.")
    else:
        print("\n[RESULT] 두 파일 간에 차이점이 발견되었습니다.")
        print("SGR_data.xlsx의 데이터가 업데이트되었거나 손상되었을 수 있습니다.")

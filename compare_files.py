import pandas as pd

print("=== SGR_data.xlsx 시트 확인 ===")
xl1 = pd.ExcelFile('SGR_data.xlsx')
print(f"시트 목록: {xl1.sheet_names}")
print()

print("=== 파이썬_SGR_데이터SET.xlsx 시트 확인 ===")
xl2 = pd.ExcelFile('파이썬_SGR_데이터SET.xlsx')
print(f"시트 목록: {xl2.sheet_names}")
print()

# 각 시트의 데이터 샘플 확인
print("=== SGR_data.xlsx 첫 번째 시트 샘플 ===")
if xl1.sheet_names:
    df1 = pd.read_excel(xl1, sheet_name=xl1.sheet_names[0])
    print(f"시트명: {xl1.sheet_names[0]}")
    print(f"Shape: {df1.shape}")
    print(df1.head())

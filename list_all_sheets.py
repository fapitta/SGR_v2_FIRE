import pandas as pd

file_path = "SGR_data.xlsx"
xls = pd.ExcelFile(file_path)

print("All sheets in SGR_data.xlsx:")
print("=" * 50)
for i, sheet in enumerate(xls.sheet_names, 1):
    print(f"{i:2d}. {sheet}")

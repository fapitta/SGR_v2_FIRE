import pandas as pd
file = 'SGR_data.xlsx'
xl = pd.ExcelFile(file)
print(xl.sheet_names)

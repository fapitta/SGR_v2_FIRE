import pandas as pd

try:
    xl = pd.ExcelFile('파이썬_SGR_데이터SET.xlsx')
    print('Sheet Names:', xl.sheet_names)
    
    df_mei = pd.read_excel('파이썬_SGR_데이터SET.xlsx', sheet_name='생산요소_물가')
    print('MEI Columns:', df_mei.columns.tolist())
    print('MEI Tail:\n', df_mei.tail())
    
    df_rv = pd.read_excel('파이썬_SGR_데이터SET.xlsx', sheet_name='상대가치변화')
    print('RV Columns:', df_rv.columns.tolist())
    print('RV Tail:\n', df_rv.tail())
    
    df_exp = pd.read_excel('파이썬_SGR_데이터SET.xlsx', sheet_name='진료비_실제')
    print('Expenditure Columns:', df_exp.columns.tolist())
    
except Exception as e:
    print(f'Error: {e}')

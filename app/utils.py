import pandas as pd
from io import BytesIO

def drop_leak(df, leak_cols):
    return df.drop(leak_cols, axis=1, errors='ignore')

def fix_gender(df):
    col = df.iloc[:,0]
    col_str = col.astype(str).str.lower()
    return col_str.replace({'1.0':1, 'male':1, '0.0':0, 'female':0}).values.reshape(-1,1)

def check_file(file_bytes, filename):
    ext = filename.split('.')[-1].lower()

    if ext == 'csv':
        df = pd.read_csv(BytesIO(file_bytes), header=None)
    elif ext in ['xls', 'xlsx']:
        df = pd.read_excel(BytesIO(file_bytes), header=None)
    else:
        raise ValueError('Файл должен быть формата .xls/.xlsx/.csv')

    df = df.dropna(how='all')          # удаляем NaN строки
    df = df.dropna(how='all', axis=1)  # удаляем NaN столбцы
    if df.shape[0] != 2:
        raise ValueError('В файле должно быть 2 строки: название и значения признаков')
    if df.shape[1] != 25:
        raise ValueError('В файле должно быть 25 столбцов (т.е. 25 признаков)')
    headers = df.iloc[0].astype(str)
    if not all(headers):
        raise ValueError('Все названия признаков должны быть непустыми строками')

    df.columns = df.iloc[0]  # ставим имена колонок
    df = df.iloc[1:]
    return df
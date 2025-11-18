import pandas as pd

def load_clean_data(file_path):
    df = pd.read_csv(file_path)

    df.columns = [col.lower().strip() for col in df.columns]

    columns = ['distrito', 'fecha', 'pm10', 'pm2_5', 'no2', 'latitud', 'longitud']
    df = df[columns]

    # Convertir fecha a tipo datetime
    df['fecha'] = pd.to_datetime(df['fecha'].astype(str), format='%Y%m%d', errors='coerce')

    for col in ['pm10', 'pm2_5', 'no2']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
    df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')

    df = df.groupby(['distrito', 'fecha', 'latitud', 'longitud'], as_index=False)[['pm10', 'pm2_5', 'no2']].mean()
    df[['pm10', 'pm2_5', 'no2']] = df[['pm10', 'pm2_5', 'no2']].round(2)
    
    return df

def latest_date(df):
    return df['fecha'].max().date()

def slice_by_date(df, date_str):
    target = pd.to_datetime(date_str).normalize()
    return df[df['fecha'] == target]
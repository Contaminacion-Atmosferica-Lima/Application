from src.data_loader import load_clean_data

# Cargar datos procesados
df = load_clean_data("data/dataset.csv")

# Mostrar resumen general
print("Datos cargados correctamente")
print("Filas totales:", len(df))
print("Columnas:", list(df.columns))
print()

# Mostrar las primeras filas
print("Primeras 10 filas:")
print(df.head(10))
print()

# Mostrar tipos de datos
print("Tipos de datos:")
print(df.dtypes)
print()

# Comprobar rangos
print("Rango de fechas:", df['fecha'].min(), "->", df['fecha'].max())
print("Rango de coordenadas:")
print("Latitud:", df['latitud'].min(), "->", df['latitud'].max())
print("Longitud:", df['longitud'].min(), "->", df['longitud'].max())
print()

# Promedios generales de contaminación
print("Promedios generales:")
print(df[['pm10', 'pm2_5', 'no2']].mean().round(2))

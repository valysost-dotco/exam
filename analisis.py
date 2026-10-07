import pandas as pd

# Cargar el archivo CSV desde la carpeta data
df = pd.read_csv("data/sensores_industriales.csv")

# Mostrar las primeras 5 filas para verificar las columnas
print("--- Primeras filas del dataset ---")
print(df.head())

# Mostrar información general del conjunto de datos (tipos de datos, nulos)
print("\n--- Información general ---")
print(df.info())

# Mostrar estadísticas descriptivas básicas
print("\n--- Resumen estadístico ---")
print(df.describe())

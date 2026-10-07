import os
import pandas as pd

# 1. Cargar el dataset con ruta relativa
ruta_csv = os.path.join("data", "sensores_industriales.csv")
df = pd.read_csv(ruta_csv)

# --- OPERACIÓN 1: Registros y sensores distintos ---
total_registros = len(df)
sensores_unicos = df["id_sensor"].nunique()
print(f"1. Cantidad de registros: {total_registros}")
print(f"   Cantidad de sensores distintos: {sensores_unicos}\n")

# --- OPERACIÓN 2: Temperatura promedio de cada planta ---
promedio_planta = df.groupby("planta")["temperatura_c"].mean()
print("2. Temperatura promedio por planta:")
print(promedio_planta.to_string())
print()

# --- OPERACIÓN 3: Temperatura máxima, sensor y fecha ---
temp_maxima = df["temperatura_c"].max()
registros_max = df[df["temperatura_c"] == temp_maxima]

print(f"3. Temperatura máxima: {temp_maxima} °C")
for _, fila in registros_max.iterrows():
    print(
        f"   Sensor: {fila['id_sensor']} | Fecha: {fila['fecha_hora']} | Planta: {fila['planta']}"
    )
print()

# --- OPERACIÓN 4: Contar lecturas con temperatura mayor que 85 °C ---
alertas_df = df[df["temperatura_c"] > 85]
total_alertas = len(alertas_df)
print(f"4. Lecturas con temperatura > 85 °C: {total_alertas}\n")

# --- OPERACIÓN 5: Planta con más alertas de temperatura (Maneja empates) ---
alertas_por_planta = alertas_df["planta"].value_counts()
max_alertas = alertas_por_planta.max()
plantas_con_mas_alertas = alertas_por_planta[
    alertas_por_planta == max_alertas
].index.tolist()

print(
    f"5. Planta(s) con más alertas ({max_alertas} alertas): {', '.join(plantas_con_mas_alertas)}\n"
)

# --- OPERACIÓN 6: Exportar lecturas con alerta a resultados/alertas.csv ---
os.makedirs("resultados", exist_ok=True)
ruta_salida = os.path.join("resultados", "alertas.csv")
alertas_df.to_csv(ruta_salida, index=False)
print(f"6. Archivo exportado exitosamente a: {ruta_salida}")

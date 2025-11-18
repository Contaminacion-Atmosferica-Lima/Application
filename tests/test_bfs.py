import sys
import os
import pandas as pd
import networkx as nx

# Para importar desde src/
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import load_clean_data, slice_by_date, latest_date
from graph_builder import build_graph
from algorithms.thresholds import classify_pollution

# ==============================
# CONFIGURACIÓN BÁSICA
# ==============================
CSV_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'dataset.csv')
THRESHOLD_KM = 15   # Distancia para conectar estaciones
POLLUTANT = "PM2_5" # Contaminante principal
MODE = "OMS"        # Modo de evaluación: "OMS" o "MINAM"

print("🧩 Iniciando pruebas del sistema de detección de islas...")
print(f"Archivo de datos: {CSV_PATH}")

# ==============================
# 1️⃣ CARGA Y LIMPIEZA DE DATOS
# ==============================
try:
    df = load_clean_data(CSV_PATH)
    print(f"✅ Datos cargados correctamente ({len(df)} filas)")
    print("Columnas:", df.columns.tolist())
    print("Fechas disponibles:", df['fecha'].min().date(), "→", df['fecha'].max().date())
except Exception as e:
    print("❌ Error al cargar los datos:", e)
    sys.exit(1)

# ==============================
# 2️⃣ SELECCIÓN DE FECHA
# ==============================
date = str(latest_date(df))
print(f"\n📅 Usando la fecha más reciente: {date}")
df_day = slice_by_date(df, date)
print(f"Filas del día seleccionado: {len(df_day)}")

# ==============================
# 3️⃣ CONSTRUCCIÓN DEL GRAFO
# ==============================
G = build_graph(df_day, distance_threshold=THRESHOLD_KM)
print(f"\n📊 Grafo construido: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")

if G.number_of_edges() == 0:
    print("⚠️ No hay conexiones entre distritos. Intenta aumentar el umbral (THRESHOLD_KM).")

# ==============================
# 4️⃣ CLASIFICACIÓN DE POLUCIÓN
# ==============================
print("\n🌈 Clasificación de contaminación:")
for node, data in G.nodes(data=True):
    value = data[POLLUTANT.lower()]
    color = classify_pollution(value, POLLUTANT, mode=MODE)
    print(f"{node:25} {POLLUTANT}: {value:6.2f} µg/m³  →  {color}")

# ==============================
# 5️⃣ DETECCIÓN DE ISLAS ROJAS
# ==============================
def detect_red_islands(G, pollutant, mode="OMS"):
    visited = set()
    islands = []
    for node, data in G.nodes(data=True):
        color = classify_pollution(data[pollutant.lower()], pollutant, mode)
        if color not in ("red", "purple") or node in visited:
            continue

        queue = [node]
        island = []
        while queue:
            current = queue.pop(0)
            if current not in visited:
                visited.add(current)
                island.append(current)
                for neighbor in G.neighbors(current):
                    n_color = classify_pollution(G.nodes[neighbor][pollutant.lower()], pollutant, mode)
                    if n_color in ("red", "purple"):
                        queue.append(neighbor)
        if island:
            islands.append(island)
    return islands

islas = detect_red_islands(G, POLLUTANT, MODE)

print("\n🔥 Resultado de detección de islas:")
if len(islas) == 0:
    print("❌ No se detectaron islas rojas.")
else:
    print(f"✅ Se detectaron {len(islas)} islas contaminadas:")
    for i, island in enumerate(islas, 1):
        print(f"  Isla {i}: {', '.join(island)}")

print("\n✅ Test completado correctamente.")

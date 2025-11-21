import pandas as pd
from src.data_loader import load_clean_data, slice_by_date, latest_date
from src.graph_builder import build_graph
from src.algorithms.bfs import detect_islands

CSV_PATH = "data/dataset.csv"

def test_bfs():
    print("\n========== TEST BFS – DETECCIÓN DE ISLAS ==========\n")

    # 1. Cargar datos
    print("Cargando dataset...")
    df = load_clean_data(CSV_PATH)

    # 2. Obtener fecha más reciente
    date = latest_date(df)
    print(f"Última fecha encontrada: {date}")

    # 3. Filtrar por esa fecha
    df_day = slice_by_date(df, str(date))

    # 4. Construir grafo
    print("Construyendo grafo con threshold = 10 km")
    G = build_graph(df_day, distance_threshold=10)

    print(f"Nodos: {len(G.nodes())}")
    print(f"Aristas: {len(G.edges())}")

    # 5. Probar distintos escenarios
    scenarios = [
        ("PM2_5", "OMS", "green"),
        ("PM2_5", "OMS", "yellow"),
        ("PM2_5", "OMS", "orange"),
        ("PM2_5", "OMS", "red"),
        ("PM2_5", "OMS", "purple"),
        ("PM10", "MINAM", "orange"),
        ("NO2", "OMS", "red")
    ]

    for pollutant, mode, severity in scenarios:
        print(f"\nProbando: pollutant={pollutant}, mode={mode}, severity={severity}")

        islands = detect_islands(G, pollutant=pollutant, mode=mode, severity=severity)

        print(f"Islas detectadas ({len(islands)}): {islands if islands else 'NINGUNA'}")

    print("\n========== FIN DEL TEST ==========\n")


if __name__ == "__main__":
    test_bfs()

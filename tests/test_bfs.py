from src.data_loader import load_clean_data, slice_by_date, latest_date
from src.graph_builder import build_graph
from src.algorithms.bfs import detect_islands

CSV = "data/dataset.csv"

def test_bfs_output_structure():
    df = load_clean_data(CSV)
    date = str(latest_date(df))
    df_day = slice_by_date(df, date)

    G = build_graph(df_day, distance_threshold=40)

    islands = detect_islands(G, pollutant="pm2_5", mode="OMS", severity="red")

    assert isinstance(islands, list)
    for isl in islands:
        assert isinstance(isl, list)
        for node in isl:
            assert node in G.nodes()

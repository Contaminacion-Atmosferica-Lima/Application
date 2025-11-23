from src.algorithms.mst import compute_mst
from src.data_loader import load_clean_data, slice_by_date, latest_date
from src.graph_builder import build_graph

CSV = "data/dataset.csv"

def test_mst_properties():
    df = load_clean_data(CSV)
    date = str(latest_date(df))
    df_day = slice_by_date(df, date)

    G = build_graph(df_day, distance_threshold=40)
    edges, weight = compute_mst(G)

    assert len(edges) == len(G.nodes()) - 1
    assert weight > 0

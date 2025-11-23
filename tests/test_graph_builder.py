from src.data_loader import load_clean_data, slice_by_date, latest_date
from src.graph_builder import build_graph

CSV = "data/dataset.csv"

def test_graph_builder():
    df = load_clean_data(CSV)
    date = str(latest_date(df))
    df_day = slice_by_date(df, date)

    G = build_graph(df_day, distance_threshold=40)

    assert len(G.nodes()) == len(df_day)
    assert len(G.edges()) > 0

def test_graph_edges_have_distance():
    df = load_clean_data(CSV)
    date = str(latest_date(df))
    df_day = slice_by_date(df, date)

    G = build_graph(df_day, distance_threshold=40)

    for u, v, d in G.edges(data=True):
        assert "weight" in d
        assert d["weight"] > 0


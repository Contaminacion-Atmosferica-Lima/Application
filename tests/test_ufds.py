from src.algorithms.ufds import UnionFind, detect_communities
from src.data_loader import load_clean_data, slice_by_date, latest_date
from src.graph_builder import build_graph

CSV = "data/dataset.csv"

def test_union_find_basic():
    uf = UnionFind(range(4))
    assert uf.find(0) == 0
    assert uf.find(3) == 3

    uf.union(0, 1)
    assert uf.find(0) == uf.find(1)

    uf.union(2, 3)
    assert uf.find(2) == uf.find(3)

    # unir ambos grupos
    uf.union(1, 2)
    root = uf.find(0)
    assert uf.find(3) == root


def test_detect_communities():
    df = load_clean_data(CSV)
    date = str(latest_date(df))
    df_day = slice_by_date(df, date)
    G = build_graph(df_day, distance_threshold=40)

    coms = detect_communities(G, pollutant="PM2_5", mode="OMS")

    assert isinstance(coms, list)

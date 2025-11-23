from src.algorithms.dijkstra import build_adj_list, dijkstra
from src.data_loader import load_clean_data, slice_by_date, latest_date
from src.graph_builder import build_graph

CSV = "data/dataset.csv"

def test_dijkstra_basic():
    df = load_clean_data(CSV)
    date = str(latest_date(df))
    df_day = slice_by_date(df, date)

    G = build_graph(df_day, distance_threshold=40)

    nodes = list(G.nodes())
    origin = nodes[0]

    edges = [(u, v, d["weight"]) for u, v, d in G.edges(data=True)]
    adj = build_adj_list(nodes, edges)

    dist = dijkstra(adj, origin)

    assert dist[origin] == 0
    assert len(dist.keys()) == len(nodes)

from src.algorithms.ufds import UnionFind

def compute_mst(G):
    if G.number_of_nodes() == 0:
        return [], 0.0

    uf = UnionFind(list(G.nodes()))

    edges_sorted = sorted(
        G.edges(data=True),
        key=lambda e: e[2].get("weight", 1)
    )

    mst_edges = []
    total_weight = 0.0

    for u, v, data in edges_sorted:
        if uf.find(u) != uf.find(v):
            uf.union(u, v)
            w = data.get("weight", 1)
            mst_edges.append((u, v, w))
            total_weight += w

    return mst_edges, round(total_weight, 2)

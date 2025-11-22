from src.algorithms.thresholds import classify_pollution


class UnionFind:
    def __init__(self, elements):
        self.parent = {e: e for e in elements}
        self.size = {e: 1 for e in elements}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return

        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra

        self.parent[rb] = ra
        self.size[ra] += self.size[rb]

    def groups(self):
        comps = {}
        for node in self.parent:
            root = self.find(node)
            if root not in comps:
                comps[root] = []
            comps[root].append(node)
        return list(comps.values())


def detect_communities(G, pollutant, mode="OMS"):
    node_color = {
        n: classify_pollution(G.nodes[n][pollutant.lower()], pollutant, mode)
        for n in G.nodes()
    }

    uf = UnionFind(list(G.nodes()))

    color_buckets = {}
    for node, color in node_color.items():
        if color not in color_buckets:
            color_buckets[color] = []
        color_buckets[color].append(node)

    for color, nodes in color_buckets.items():
        for i in range(1, len(nodes)):
            uf.union(nodes[0], nodes[i])

    raw_groups = uf.groups()

    communities = []
    for group in raw_groups:
        if not group:
            continue

        color = node_color[group[0]]

        group_sorted = sorted(group)

        communities.append({
            "color": color,
            "nodes": group_sorted
        })

    communities.sort(key=lambda x: len(x["nodes"]), reverse=True)

    return communities

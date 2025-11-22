from collections import deque
from src.algorithms.thresholds import classify_pollution

SEVERITY_MAP = {
    "green":  ["green"],
    "yellow": ["yellow", "orange", "red", "purple"],
    "orange": ["orange", "red", "purple"],
    "red":    ["red", "purple"],
    "purple": ["purple"]
}

def detect_islands(G, pollutant, mode="OMS", severity="red"):
    visited = set()
    islands = []

    target_colors = SEVERITY_MAP.get(severity.lower(), ["red", "purple"])

    node_color = {
        n: classify_pollution(G.nodes[n][pollutant.lower()], pollutant, mode)
        for n in G.nodes()
    }

    for node in G.nodes():
        if node in visited:
            continue

        if node_color[node] not in target_colors:
            continue

        queue = deque([node])
        island = []

        while queue:
            current = queue.popleft()

            if current in visited:
                continue

            visited.add(current)
            island.append(current)

            for neighbor in G.neighbors(current):
                if neighbor not in visited and node_color[neighbor] in target_colors:
                    queue.append(neighbor)

        if island:
            islands.append(island)

    return islands

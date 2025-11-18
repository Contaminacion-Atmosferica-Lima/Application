import networkx as nx
from src.algorithms.thresholds import classify_pollution

def detect_red_islands(G, pollutant, mode="OMS", severity="red"):
    visited = set()
    islands = []

    target_colors = ["red", "purple"] if severity == "red" else ["orange", "red", "purple"]

    for node, data in G.nodes(data=True):
        color = classify_pollution(data[pollutant.lower()], pollutant, mode)
        if color not in target_colors or node in visited:
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
                    if n_color in target_colors:
                        queue.append(neighbor)
        if island:
            islands.append(island)
    return islands


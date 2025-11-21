from src.algorithms.thresholds import classify_pollution

SEVERITY_MAP = {
    "green":   ["green", "yellow", "orange", "red", "purple"],
    "yellow":  ["yellow", "orange", "red", "purple"],
    "orange":  ["orange", "red", "purple"],
    "red":     ["red", "purple"],
    "purple":  ["purple"]
}

def detect_islands(G, pollutant, mode="OMS", severity="red"):
    visited = set()
    islands = []

    target_colors = SEVERITY_MAP.get(severity.lower(), ["red", "purple"])

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
                    neighbor_color = classify_pollution(
                        G.nodes[neighbor][pollutant.lower()],
                        pollutant,
                        mode
                    )
                    if neighbor_color in target_colors:
                        queue.append(neighbor)

        if island:
            islands.append(island)

    return islands

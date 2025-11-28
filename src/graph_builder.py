import networkx as nx
from math import radians, sin, cos, sqrt, asin

def haversine(lat1, lon1, lat2, lon2):
    # Convertir latitudes y longitudes de grados a radianes
    lat1_rad = radians(lat1)
    lon1_rad = radians(lon1)
    lat2_rad = radians(lat2)
    lon2_rad = radians(lon2)

    # Formula de Haversine
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))

    r = 6371.0
    return c * r


def build_graph(df, distance_threshold=10):
    G = nx.Graph()

    for _, row in df.iterrows():
        date_str = row["fecha"].strftime("%Y-%m-%d")
        district_id = row["distrito"].upper().replace(" ", "_")
        node_id = f"{district_id}_{date_str}"

        avg_value = (row["pm2_5"] + row["pm10"] + row["no2"]) / 3

        G.add_node(
            node_id,
            distrito=row["distrito"],
            latitud=row["latitud"],
            longitud=row["longitud"],
            pm10=row["pm10"],
            pm2_5=row["pm2_5"],
            no2=row["no2"],
            avg=round(avg_value, 2),
            fecha=date_str
        )

    entries = []
    for _, row in df.iterrows():
        district_id = row["distrito"].upper().replace(" ", "_")
        node_id = f"{district_id}_{row['fecha'].strftime('%Y-%m-%d')}"
        entries.append((node_id, row["latitud"], row["longitud"]))

    for i in range(len(entries)):
        id1, lat1, lon1 = entries[i]
        for j in range(i + 1, len(entries)):
            id2, lat2, lon2 = entries[j]
            dist = haversine(lat1, lon1, lat2, lon2)

            if dist <= distance_threshold:
                G.add_edge(id1, id2, weight=round(dist, 2))

    return G


def build_global_graph(df, distance_threshold=10):
    G = nx.Graph()

    for _, row in df.iterrows():
        date_str = row["fecha"].strftime("%Y-%m-%d")
        district_id = row["distrito"].upper().replace(" ", "_")
        node_id = f"{district_id}_{date_str}"

        G.add_node(
            node_id,
            distrito=row["distrito"],
            latitud=row["latitud"],
            longitud=row["longitud"],
            pm10=row["pm10"],
            pm2_5=row["pm2_5"],
            no2=row["no2"],
            fecha=date_str
        )

    grouped = df.groupby("fecha")

    for date, group in grouped:
        entries = []
        for _, row in group.iterrows():
            district_id = row["distrito"].upper().replace(" ", "_")
            node_id = f"{district_id}_{date.strftime('%Y-%m-%d')}"
            entries.append((node_id, row["latitud"], row["longitud"]))

        for i in range(len(entries)):
            id1, lat1, lon1 = entries[i]
            for j in range(i + 1, len(entries)):
                id2, lat2, lon2 = entries[j]
                dist = haversine(lat1, lon1, lat2, lon2)

                if dist <= distance_threshold:
                    G.add_edge(id1, id2, weight=round(dist, 2))

    distritos = df["distrito"].unique()
    for distrito in distritos:
        sub = df[df["distrito"] == distrito].sort_values("fecha")
        rows = list(sub.iterrows())

        for i in range(len(rows) - 1):
            _, row1 = rows[i]
            _, row2 = rows[i + 1]

            date1 = row1["fecha"].strftime("%Y-%m-%d")
            date2 = row2["fecha"].strftime("%Y-%m-%d")

            id1 = distrito.upper().replace(" ", "_") + "_" + date1
            id2 = distrito.upper().replace(" ", "_") + "_" + date2

            G.add_edge(id1, id2, weight=1)

    return G
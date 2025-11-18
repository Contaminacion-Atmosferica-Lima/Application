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
        G.add_node(
            row['distrito'],
            latitud=row['latitud'],
            longitud=row['longitud'],
            pm10=row['pm10'],
            pm2_5=row['pm2_5'],
            no2=row['no2'],
            fecha=row['fecha']
        )

    distritos = df[['distrito', 'latitud', 'longitud']].values

    for i in range(len(distritos)):
        est1, lat1, lon1 = distritos[i]
        for j in range(i + 1, len(distritos)):
            est2, lat2, lon2 = distritos[j]
            dist = haversine(lat1, lon1, lat2, lon2)

            if dist <= distance_threshold:
                G.add_edge(est1, est2, weight=round(dist, 2))

    return G
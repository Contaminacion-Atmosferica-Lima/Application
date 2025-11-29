from flask import Flask, jsonify, request, render_template
from flasgger import swag_from, Swagger
from src.data_loader import load_clean_data, latest_date, slice_by_date
from src.graph_builder import build_graph, build_global_graph
from src.algorithms.bfs import detect_islands
from src.algorithms.thresholds import classify_pollution
from src.algorithms.ufds import detect_communities
from src.algorithms.mst import compute_mst
from src.algorithms.dijkstra import build_adj_list, dijkstra

app = Flask(__name__)
swagger = Swagger(app)

CSV_PATH = 'data/dataset.csv'
_df_cache = None

def get_df():
    global _df_cache
    if _df_cache is None:
        _df_cache = load_clean_data(CSV_PATH)
    return _df_cache

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ping')
def ping():
    return jsonify({'message': 'Servidor flask funcionando correctamente'})

@app.route('/api/data')
def get_data():
    df = get_df()
    date = request.args.get('date')
    if date:
        df = slice_by_date(df, date)
    return df.to_json(orient='records', date_format='iso')

@swag_from("docs/graph.yml")
@app.route('/api/graph')
def get_graph():
    df = get_df()

    pollutant = request.args.get("pollutant", "PM2_5").upper()
    mode = request.args.get("mode", "OMS").upper()

    date = request.args.get('date')
    threshold = float(request.args.get('th', 10))

    if date:
        df_slice = slice_by_date(df, date)
    else:
        date = str(latest_date(df))
        df_slice = slice_by_date(df, date)

    G = build_graph(df_slice, distance_threshold=threshold)

    nodes_json = []
    for node_id, data in G.nodes(data=True):

        value = data[pollutant.lower()]

        color = classify_pollution(value, pollutant, mode)

        nodes_json.append({
            "id": node_id,
            "distrito": data["distrito"],
            "fecha": data["fecha"],
            "latitud": data["latitud"],
            "longitud": data["longitud"],
            "pm10": data["pm10"],
            "pm2_5": data["pm2_5"],
            "no2": data["no2"],
            "avg": data["avg"], 
            "color": color
        })

    edges_json = [
        {
            "source": u,
            "destination": v,
            "distance": d["weight"]
        }
        for u, v, d in G.edges(data=True)
    ]

    return jsonify({
        "date": date,
        "pollutant": pollutant,
        "mode": mode,
        "nodes": nodes_json,
        "edges": edges_json
    })

@swag_from("docs/islas.yml")
@app.route("/api/islas")
def get_islas():
    pollutant = request.args.get("pollutant", "PM2_5")
    mode = request.args.get("mode", "OMS")
    date = request.args.get("date")
    severity = request.args.get("severity", "red").lower()

    pollutant = pollutant.replace(".", "_").lower()

    try:
        threshold = float(request.args.get("th", 10))
    except:
        threshold = 10

    df = get_df()

    if date:
        df_slice = slice_by_date(df, date)
    else:
        date = str(latest_date(df))
        df_slice = slice_by_date(df, date)

    G = build_graph(df_slice, distance_threshold=threshold)

    islands = detect_islands(
        G,
        pollutant=pollutant,
        mode=mode,
        severity=severity
    )

    return jsonify({
        "date": date,
        "pollutant": pollutant,
        "mode": mode,
        "severity": severity,
        "islands": islands,
        "count": len(islands)
    })

@swag_from("docs/communities.yml")
@app.route("/api/communities")
def get_communities():
    df = get_df()

    pollutant = request.args.get("pollutant", "PM2_5").upper()
    mode = request.args.get("mode", "OMS").upper()
    date = request.args.get("date")
    threshold = float(request.args.get("th", 10))  

    if date:
        df_slice = slice_by_date(df, date)
    else:
        date = str(latest_date(df))
        df_slice = slice_by_date(df, date)

    G = build_graph(df_slice, distance_threshold=threshold)

    communities = detect_communities(G, pollutant=pollutant, mode=mode)

    return jsonify({
        "date": date,
        "pollutant": pollutant,
        "mode": mode,
        "communities": communities,
        "count": len(communities)
    })

@swag_from("docs/mst.yml")
@app.route("/api/mst")
def get_mst():
    df = get_df()

    date = request.args.get("date")
    threshold = 40.0

    if date:
        df_slice = slice_by_date(df, date)
    else:
        date = str(latest_date(df))
        df_slice = slice_by_date(df, date)

    G = build_graph(df_slice, distance_threshold=threshold)

    mst_edges, total_weight = compute_mst(G)

    edges_json = [
        {
            "source": u,
            "destination": v,
            "distance": w
        }
        for u, v, w in mst_edges
    ]

    return jsonify({
        "date": date,
        "threshold": threshold,
        "node_count": len(G.nodes()),
        "edge_count": len(G.edges()),
        "mst_edge_count": len(edges_json),
        "total_weight": total_weight,
        "edges": edges_json
    })

@swag_from("docs/propagation.yml")
@app.route("/api/propagation")
def propagation():
    df = get_df()
    date = request.args.get("date")
    origin = request.args.get("origin") 
    threshold = 40.0  # Grafo completo

    if not origin:
        return jsonify({"error": "origin parameter is required"}), 400

    if date:
        df_slice = slice_by_date(df, date)
    else:
        date = str(latest_date(df))
        df_slice = slice_by_date(df, date)

    G = build_graph(df_slice, distance_threshold=threshold)

    origin_clean = origin.upper().replace(" ", "_")
    origin_id = f"{origin_clean}_{date}"

    if origin_id not in G.nodes():
        return jsonify({
            "error": "The origin district does not exist for the selected date",
            "origin_received": origin,
            "origin_built": origin_id,
            "available_nodes": list(G.nodes())
        }), 400

    nodes = list(G.nodes())
    edges = [(u, v, d["weight"]) for u, v, d in G.edges(data=True)]

    adj = build_adj_list(nodes, edges)
    dist = dijkstra(adj, origin_id)

    ordered = sorted(dist.items(), key=lambda x: x[1])

    return jsonify({
        "date": date,
        "origin": origin_id,
        "distances": dist,
        "order": [node for node, d in ordered]
    })

@swag_from("docs/global_graph.yml")
@app.route('/api/global_graph')
def api_global_graph():
    df = get_df()

    distrito = request.args.get("distrito")
    pollutant = request.args.get("pollutant", "PM2_5").upper()
    mode = request.args.get("mode", "OMS").upper()
    threshold = float(request.args.get("th", 10))

    if distrito:
        df = df[df["distrito"].str.upper() == distrito.upper()]

    G = build_global_graph(df, distance_threshold=threshold)

    nodes_json = []
    for node_id, data in G.nodes(data=True):

        if pollutant == "PM10":
            value = data["pm10"]
        elif pollutant in ["PM2_5", "PM2.5"]:
            value = data["pm2_5"]
        elif pollutant == "NO2":
            value = data["no2"]
        else:
            value = data["avg"]

        color = classify_pollution(value, pollutant, mode)

        nodes_json.append({
            "id": node_id,
            "distrito": data["distrito"],
            "fecha": data["fecha"],
            "latitud": data["latitud"],
            "longitud": data["longitud"],
            "pm10": data["pm10"],
            "pm2_5": data["pm2_5"],
            "no2": data["no2"],
            "avg": data["avg"],
            "color": color
        })

    edges_json = [
        {"source": u, "destination": v, "distance": d["weight"]}
        for u, v, d in G.edges(data=True)
    ]

    return jsonify({
        "total_nodes": len(nodes_json),
        "total_edges": len(edges_json),
        "nodes": nodes_json,
        "edges": edges_json
    })


@app.route('/global_viewer')
def global_viewer():
    return render_template('global_graph.html')


if __name__ == '__main__':
    app.run(debug=True)
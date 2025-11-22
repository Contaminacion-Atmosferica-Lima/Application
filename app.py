from flask import Flask, jsonify, request, render_template
from src.data_loader import load_clean_data, latest_date, slice_by_date
from src.graph_builder import build_graph, build_global_graph
from src.algorithms.bfs import detect_islands
from src.algorithms.thresholds import classify_pollution
from src.algorithms.ufds import detect_communities
from src.algorithms.mst import compute_mst


app = Flask(__name__)

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

@app.route("/api/mst")
def get_mst():
    df = get_df()

    date = request.args.get("date")
    try:
        threshold = float(request.args.get("th", 40))
    except:
        threshold = 40

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



@app.route('/api/global_graph')
def get_global_graph():
    df = get_df()
    threshold = float(request.args.get('th', 10))

    G = build_global_graph(df, distance_threshold=threshold)

    graph_json = {
        'total_nodes': len(G.nodes()),
        'total_edges': len(G.edges()),
        'nodes': [{'id': n, **G.nodes[n]} for n in G.nodes()],
        'edges': [
            {'source': u, 'destination': v, 'distance': d['weight']}
            for u, v, d in G.edges(data=True)
        ]
    }

    return jsonify(graph_json)



if __name__ == '__main__':
    app.run(debug=True)
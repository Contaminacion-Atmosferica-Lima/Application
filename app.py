from flask import Flask, jsonify, request, render_template
from src.data_loader import load_clean_data, latest_date, slice_by_date
from src.graph_builder import build_graph
from src.algorithms.bfs import detect_islands
import pandas as pd

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
    date = request.args.get('date')
    threshold = float(request.args.get('th', 10))

    if date:
        df = slice_by_date(df, date)
    else:
        date = str(latest_date(df))
        df = slice_by_date(df, date)

    G = build_graph(df, distance_threshold=threshold)

    graph_json = {
        'date': date,
        'nodes': [{'id': n, **G.nodes[n]} for n in G.nodes()],
        'edges': [{'source': u, 'destination': v, 'distance': d['weight']} for u, v, d in G.edges(data=True)]
    }

    return jsonify(graph_json)

@app.route("/api/islas")
def get_islas():
    pollutant = request.args.get("pollutant", "PM2_5")
    mode = request.args.get("mode", "OMS")
    date = request.args.get("date")
    threshold = float(request.args.get("th", 10))
    severity = request.args.get("severity", "red") 

    df = load_clean_data("data/dataset.csv")

    if date:
        df = slice_by_date(df, date)
    else:
        date = str(latest_date(df))
        df = slice_by_date(df, date)

    G = build_graph(df, distance_threshold=threshold)

    islands = detect_islands(G, pollutant=pollutant, mode=mode, severity=severity)

    return jsonify({
        "date": date,
        "pollutant": pollutant,
        "mode": mode,
        "severity": severity,      
        "islands": islands,
        "count": len(islands)
    })

if __name__ == '__main__':
    app.run(debug=True)
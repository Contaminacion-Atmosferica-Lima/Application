import pytest
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_api_graph(client):
    r = client.get("/api/graph?date=2024-05-31")
    assert r.status_code == 200
    assert "nodes" in r.json

def test_api_islas(client):
    r = client.get("/api/islas?date=2024-05-31&pollutant=PM2_5")
    assert r.status_code == 200
    assert "islands" in r.json

def test_api_communities(client):
    r = client.get("/api/communities?date=2024-05-31")
    assert r.status_code == 200

def test_api_mst(client):
    r = client.get("/api/mst?date=2024-05-31")
    assert r.status_code == 200
    assert "edges" in r.json

def test_api_propagation(client):
    r = client.get("/api/propagation?origin=San_Borja&date=2024-05-31")
    assert r.status_code == 200

def test_api_data(client):
    r = client.get("/api/data?date=2024-05-31")
    assert r.status_code == 200

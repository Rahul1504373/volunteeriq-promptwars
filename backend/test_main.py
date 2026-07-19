from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_ask():
    r = client.post("/ask", json={"fan_query":"Where is gate A?","volunteer_gate":"gate_a","match_id":"WC01"})
    assert r.status_code == 200
    assert "fan_response" in r.json()

def test_crowd():
    r = client.post("/crowd", json={"match_id":"WC01"})
    assert r.status_code == 200
    assert "analysis" in r.json()

def test_facilities():
    r = client.get("/facilities")
    assert r.status_code == 200

def test_briefing():
    r = client.get("/briefing/gate_a/WC01")
    assert r.status_code == 200
    assert "briefing" in r.json()

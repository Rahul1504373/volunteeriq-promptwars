from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["agents"] == 4

def test_ask_returns_response():
    r = client.post("/ask", json={
        "fan_query": "Where is gate A?",
        "volunteer_gate": "gate_a",
        "match_id": "WC01"
    })
    assert r.status_code == 200
    assert "fan_response" in r.json()
    assert "volunteer_summary" in r.json()

def test_crowd_analysis():
    r = client.post("/crowd", json={"match_id": "WC01"})
    assert r.status_code == 200
    assert "gates_live" in r.json()
    assert "analysis" in r.json()

def test_facilities_default():
    r = client.get("/facilities")
    assert r.status_code == 200
    assert "food" in r.json()

def test_facilities_halal_filter():
    r = client.get("/facilities?halal=true")
    assert r.status_code == 200

def test_briefing_valid_gate():
    r = client.get("/briefing/gate_a/WC01")
    assert r.status_code == 200
    assert "briefing" in r.json()

def test_briefing_invalid_gate():
    r = client.get("/briefing/invalid_gate/WC01")
    assert r.status_code == 404

def test_incident_medical():
    r = client.get("/incident/medical")
    assert r.status_code == 200
    assert "protocol" in r.json()

def test_accessibility():
    r = client.post("/accessibility", json={
        "fan_query": "I need wheelchair access",
        "current_location": "Gate A"
    })
    assert r.status_code == 200
    assert "fan_instructions" in r.json()

def test_security_headers():
    r = client.get("/health")
    assert "x-content-type-options" in r.headers

from fastapi.testclient import TestClient
from app.main import app
from app.services import alert_dispatcher
from app.db import timeseries

def test_predict_basic(monkeypatch):
    # stub DB write and alert sending so test is deterministic and fast
    monkeypatch.setattr(timeseries, "write_telemetry", lambda rec: None)
    monkeypatch.setattr(alert_dispatcher.AlertDispatcher, "send_alert", lambda payload: None)

    client = TestClient(app)
    payload = {
        "records": [
            {"device_id": "d1", "ts": 1.0, "value": 20.0, "meta": {}}
        ]
    }
    r = client.post("/predict/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    rec = data[0]
    assert rec["device_id"] == "d1"
    assert "p_fail" in rec
    assert isinstance(rec["p_fail"], float)

def test_predict_triggers_alert_when_threshold_exceeded(monkeypatch):
    # capture calls to send_alert
    called = []
    def fake_send(payload):
        called.append(payload)

    monkeypatch.setattr(timeseries, "write_telemetry", lambda rec: None)
    monkeypatch.setattr(alert_dispatcher.AlertDispatcher, "send_alert", fake_send)

    client = TestClient(app)
    # value big enough to cause p_fail > 0.5 given stub logic (value_norm ~ value/100)
    payload = {
        "records": [
            {"device_id": "d_alert", "ts": 1.0, "value": 80.0, "meta": {}}
        ]
    }
    r = client.post("/predict/", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    assert len(data) == 1
    # ensure alert was triggered
    assert len(called) == 1
    assert called[0]["device_id"] == "d_alert"
    assert "p_fail" in called[0]

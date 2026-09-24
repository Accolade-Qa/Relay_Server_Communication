from fastapi.testclient import TestClient

from server.main import app


client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_command_endpoint_valid():
    payload = {"request_id": "req-123", "command": "1011"}
    headers = {"X-Client-ID": "client_a", "Authorization": "Bearer demo-client-a-key"}
    response = client.post("/command", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["command"] == "1011"
    assert body["actual_state"] == "1011"


def test_command_endpoint_invalid():
    payload = {"request_id": "req-456", "command": "1012"}
    headers = {"X-Client-ID": "client_a", "Authorization": "Bearer demo-client-a-key"}
    response = client.post("/command", json=payload, headers=headers)
    assert response.status_code == 400
    body = response.json()
    assert body["success"] is False
    assert body["error_code"] == "INVALID_COMMAND"


def test_lan_request_without_identity_is_allowed():
    payload = {"request_id": "req-789", "command": "1011"}
    headers = {"X-Client-ID": "phone-guest", "Authorization": "Bearer ignored-for-lan"}
    response = client.post("/command", json=payload, headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True


def test_status_endpoint_reports_state():
    response = client.get("/status")
    assert response.status_code == 200
    body = response.json()
    assert body["server_status"] == "running"
    assert "requested_state" in body
    assert "actual_state" in body

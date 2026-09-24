from fastapi.testclient import TestClient

from server.main import app


client = TestClient(app)


def test_lan_client_without_auth_works():
    response = client.post(
        "/command",
        json={"request_id": "lan-1", "command": "1011"},
        headers={},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_lan_phone_can_send_command_without_identity():
    response = client.post(
        "/command",
        json={"request_id": "phone-001", "command": "0000"},
        headers={"Authorization": "Bearer ignored-for-lan"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_missing_request_id_is_rejected():
    response = client.post(
        "/command",
        json={"command": "0000"},
        headers={},
    )
    assert response.status_code == 422

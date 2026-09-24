from __future__ import annotations

from typing import Any

from server.database import Database


def verify_client_identity(client_id: str | None, api_key: str | None, db: Database | None = None) -> dict[str, Any]:
    db = db or Database()
    if not client_id:
        return {"valid": False, "error_code": "UNKNOWN_CLIENT", "message": "Missing client ID."}

    client = db.get_client(client_id)
    if not client:
        return {"valid": False, "error_code": "UNKNOWN_CLIENT", "message": "Client is not recognized."}

    if api_key is None or str(api_key).strip() == "":
        return {"valid": False, "error_code": "UNAUTHORIZED_CLIENT", "message": "Missing API key."}

    if api_key != client["api_key_hash"]:
        return {"valid": False, "error_code": "INVALID_CREDENTIAL", "message": "API key is invalid."}

    return {"valid": True, "client": client}


def authorize_command(client: dict[str, Any], command: str) -> dict[str, Any]:
    allowed = client.get("allowed_commands") or "all"
    if allowed == "all":
        return {"authorized": True}

    allowed_set = {value.strip() for value in allowed.split(",") if value.strip()}
    if command in allowed_set:
        return {"authorized": True}

    return {"authorized": False, "error_code": "UNAUTHORIZED_COMMAND", "message": "Client is not allowed to send this command."}

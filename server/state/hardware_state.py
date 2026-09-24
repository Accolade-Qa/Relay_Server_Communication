from __future__ import annotations

from server.database import Database


class HardwareStateManager:
    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    def get_status(self):
        row = self.db.get_server_state()
        if not row:
            return {"server_status": "running", "hardware_connected": 0, "requested_state": "0000", "actual_state": "0000", "queue_length": 0}
        return {
            "server_status": row["server_status"],
            "hardware_connected": bool(row["hardware_connected"]),
            "requested_state": row["requested_state"],
            "actual_state": row["actual_state"],
            "queue_length": 0,
        }

    def update_requested_state(self, command: str):
        current = self.db.get_server_state()
        if current is None:
            current = {"requested_state": "0000", "actual_state": "0000", "hardware_connected": 0, "server_status": "running"}
        self.db.update_server_state(requested_state=command, actual_state=current["actual_state"], hardware_connected=current["hardware_connected"], server_status=current["server_status"])

    def update_actual_state(self, command: str):
        current = self.db.get_server_state()
        if current is None:
            current = {"requested_state": "0000", "actual_state": "0000", "hardware_connected": 0, "server_status": "running"}
        self.db.update_server_state(requested_state=current["requested_state"], actual_state=command, hardware_connected=current["hardware_connected"], server_status=current["server_status"])

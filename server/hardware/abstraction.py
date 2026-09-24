import threading
from server.database import Database


class SimulatedHardware:
    _lock = threading.Lock()

    def __init__(self, db: Database | None = None):
        self.db = db or Database()

    def execute_command(self, command: str) -> dict:
        with self._lock:
            actual_state = command
            status = "accepted"
            message = "Command executed by simulated hardware controller."
            return {"actual_state": actual_state, "status": status, "message": message}


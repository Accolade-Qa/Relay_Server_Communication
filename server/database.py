from __future__ import annotations

import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent.parent / "control_system.db"


class Database:
    def __init__(self, db_path: str | Path = DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        conn = self._connect()
        try:
            self._ensure_command_history_schema(conn)
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS server_state (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    requested_state TEXT NOT NULL DEFAULT '0000',
                    actual_state TEXT NOT NULL DEFAULT '0000',
                    hardware_connected INTEGER NOT NULL DEFAULT 0,
                    server_status TEXT NOT NULL DEFAULT 'running'
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS command_status (
                    request_id TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    updated_at TEXT NOT NULL,
                    message TEXT
                )
                """
            )
            conn.execute(
                "INSERT OR IGNORE INTO server_state (id, requested_state, actual_state, hardware_connected, server_status) VALUES (1, '0000', '0000', 0, 'running')"
            )
            conn.commit()
        finally:
            conn.close()

    def _ensure_command_history_schema(self, conn):
        table_exists = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='command_history'"
        ).fetchone()
        if not table_exists:
            conn.execute(
                """
                CREATE TABLE command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    result TEXT
                )
                """
            )
            return

        table_sql = conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='command_history'"
        ).fetchone()
        if table_sql and 'UNIQUE' in (table_sql[0] or ''):
            conn.execute("ALTER TABLE command_history RENAME TO command_history_legacy")
            conn.execute(
                """
                CREATE TABLE command_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    client_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    result TEXT
                )
                """
            )
            conn.execute(
                "INSERT INTO command_history (request_id, client_id, command, status, created_at, completed_at, result) SELECT request_id, client_id, command, status, created_at, completed_at, result FROM command_history_legacy"
            )
            conn.execute("DROP TABLE command_history_legacy")

    def get_server_state(self):
        conn = self._connect()
        try:
            row = conn.execute("SELECT * FROM server_state WHERE id = 1").fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def update_server_state(self, requested_state: str, actual_state: str | None = None, hardware_connected: int | None = None, server_status: str | None = None):
        conn = self._connect()
        try:
            current = self.get_server_state()
            if current is None:
                current = {"requested_state": "0000", "actual_state": "0000", "hardware_connected": 0, "server_status": "running"}
            if actual_state is None:
                actual_state = current["actual_state"]
            if hardware_connected is None:
                hardware_connected = current["hardware_connected"]
            if server_status is None:
                server_status = current["server_status"]
            conn.execute(
                "UPDATE server_state SET requested_state = ?, actual_state = ?, hardware_connected = ?, server_status = ? WHERE id = 1",
                (requested_state, actual_state, hardware_connected, server_status),
            )
            conn.commit()
        finally:
            conn.close()

    def add_command_log(self, request_id: str, client_id: str, command: str, status: str, created_at: str, completed_at: str | None = None, result: str | None = None):
        conn = self._connect()
        try:
            conn.execute(
                "INSERT INTO command_history (request_id, client_id, command, status, created_at, completed_at, result) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (request_id, client_id, command, status, created_at, completed_at, result),
            )
            conn.commit()
        finally:
            conn.close()

    def update_command_status(self, request_id: str, client_id: str, command: str, status: str, message: str | None = None):
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT INTO command_status (request_id, client_id, command, status, updated_at, message)
                VALUES (?, ?, ?, ?, datetime('now'), ?)
                ON CONFLICT(request_id) DO UPDATE SET
                    client_id = excluded.client_id,
                    command = excluded.command,
                    status = excluded.status,
                    updated_at = datetime('now'),
                    message = excluded.message
                """,
                (request_id, client_id, command, status, message),
            )
            conn.commit()
        finally:
            conn.close()

    def get_command_status(self, request_id: str):
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT * FROM command_status WHERE request_id = ?",
                (request_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

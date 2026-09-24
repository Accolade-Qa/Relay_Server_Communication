from datetime import datetime, timezone

from server.command.queue import command_queue
from server.command.validator import validate_command
from server.database import Database
from server.hardware.abstraction import SimulatedHardware
from server.state.hardware_state import HardwareStateManager


def process_command_request(request_id: str, command: str, client_id: str | None = None, api_key: str | None = None) -> dict:
    db = Database()

    validation = validate_command(command)
    if not validation["valid"]:
        return {
            "request_id": request_id,
            "success": False,
            "command": command,
            "actual_state": None,
            "message": validation["error"],
            "error_code": "INVALID_COMMAND",
        }

    queue_result = command_queue.enqueue({
        "request_id": request_id,
        "client_id": client_id or "lan-client",
        "command": command,
        "queued_at": datetime.now(timezone.utc).isoformat(),
    })
    if not queue_result["accepted"]:
        return {
            "request_id": request_id,
            "success": False,
            "command": command,
            "actual_state": None,
            "message": queue_result["message"],
            "error_code": queue_result["error_code"],
        }

    state = HardwareStateManager(db)
    state.update_requested_state(command)

    hardware = SimulatedHardware(db=db)
    hardware_result = hardware.execute_command(command)
    state.update_actual_state(hardware_result["actual_state"])

    db.add_command_log(
        request_id=request_id,
        client_id=client_id or "lan-client",
        command=command,
        status=hardware_result["status"],
        created_at=datetime.now(timezone.utc).isoformat(),
        completed_at=datetime.now(timezone.utc).isoformat(),
        result=hardware_result["status"],
    )
    db.update_command_status(
        request_id=request_id,
        client_id=client_id or "lan-client",
        command=command,
        status=hardware_result["status"],
        message=hardware_result["message"],
    )

    return {
        "request_id": request_id,
        "success": True,
        "command": command,
        "actual_state": command,
        "message": "Command accepted and validated.",
        "error_code": None,
    }

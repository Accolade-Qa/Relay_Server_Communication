from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from server.api.schemas import CommandRequest, CommandResponse, HealthResponse, StatusResponse
from server.command.processor import process_command_request
from server.command.queue import command_queue
from server.database import Database
from server.state.hardware_state import HardwareStateManager

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health() -> dict:
    return {"status": "ok"}


@router.get("/status", response_model=StatusResponse)
def status_endpoint() -> dict:
    state = HardwareStateManager(Database()).get_status()
    state["queue_length"] = command_queue.size()
    return state


@router.post("/command", response_model=CommandResponse)
def process_command(request: Request, payload: CommandRequest):
    client_id = request.headers.get("X-Client-ID") or "lan-client"
    api_key = request.headers.get("Authorization", "")
    result = process_command_request(payload.request_id, payload.command, client_id, api_key)

    if not result["success"]:
        status_code = status.HTTP_400_BAD_REQUEST
        return JSONResponse(
            status_code=status_code,
            content={
                "success": False,
                "error_code": result["error_code"],
                "message": result["message"],
                "request_id": payload.request_id,
                "command": payload.command,
            },
        )
    return result


@router.get("/command/{request_id}/status")
def get_command_status(request_id: str):
    db = Database()
    row = db.get_command_status(request_id)
    if not row:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"request_id": request_id, "status": "not_found", "message": "Command status not found."},
        )
    return {
        "request_id": row["request_id"],
        "client_id": row["client_id"],
        "command": row["command"],
        "status": row["status"],
        "updated_at": row["updated_at"],
        "message": row["message"],
    }

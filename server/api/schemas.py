from pydantic import BaseModel, Field, field_validator


class CommandRequest(BaseModel):
    request_id: str = Field(..., min_length=1)
    command: str = Field(..., min_length=1, max_length=10)

    @field_validator("command")
    @classmethod
    def validate_command_text(cls, value: str) -> str:
        if not value:
            raise ValueError("Command must not be empty.")
        return value.strip()


class CommandResponse(BaseModel):
    request_id: str
    success: bool
    command: str
    actual_state: str
    message: str | None = None
    error_code: str | None = None


class HealthResponse(BaseModel):
    status: str


class StatusResponse(BaseModel):
    server_status: str
    hardware_connected: bool
    requested_state: str
    actual_state: str
    queue_length: int

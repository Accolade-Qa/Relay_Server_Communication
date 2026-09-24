from dataclasses import dataclass


@dataclass
class ServerSettings:
    host: str = "0.0.0.0"
    port: int = 8000
    command_length: int = 4
    hardware_timeout_seconds: float = 2.0
    command_queue_size: int = 100


settings = ServerSettings()

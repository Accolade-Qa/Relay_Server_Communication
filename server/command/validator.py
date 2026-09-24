import re


def validate_command(command: str) -> dict:
    """Validate that a command is a 4-bit binary string and return structured output."""
    if command is None:
        return {"valid": False, "error": "Command is required.", "bits": None}

    if not isinstance(command, str):
        return {"valid": False, "error": "Command must be a string.", "bits": None}

    if len(command) != 4:
        return {"valid": False, "error": "Command must contain exactly 4 characters.", "bits": None}

    if not re.fullmatch(r"[01]{4}", command):
        return {"valid": False, "error": "Command must contain only 0 and 1 characters.", "bits": None}

    bits = {
        "output_1": command[0] == "1",
        "output_2": command[1] == "1",
        "output_3": command[2] == "1",
        "output_4": command[3] == "1",
    }

    return {"valid": True, "error": None, "bits": bits}

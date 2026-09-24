# Control System Prototype

This project is the first phase of a server-client hardware control system.
It implements the local LAN prototype without physical hardware.

## Architecture

Client -> HTTP API -> Validation -> Response

The server accepts a 4-bit binary command such as `1011`, validates it, and responds with success or an error.

For same-network use, the system is intentionally designed to trust local LAN traffic without requiring a full identity or authorization system.

## Directory structure

```text
CONTROL_SYSTEM/
├── server/
│   ├── __init__.py
│   ├── config.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── schemas.py
│   └── command/
│       ├── __init__.py
│       └── validator.py
├── client/
│   ├── __init__.py
│   ├── main.py
│   └── client_api.py
├── tests/
│   ├── test_api.py
│   └── test_validator.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Create environment on Windows

```powershell
cd d:\AEPL_AUTOMATION\Communication
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run server

```powershell
cd d:\AEPL_AUTOMATION\Communication
.\.venv\Scripts\Activate.ps1
python -m uvicorn server.main:app --host 0.0.0.0 --port 8000
```

## Run client

```powershell
cd d:\AEPL_AUTOMATION\Communication
.\.venv\Scripts\Activate.ps1
python client/main.py 1011
```

## Test suite

```powershell
cd d:\AEPL_AUTOMATION\Communication
.\.venv\Scripts\Activate.ps1
pytest -q
```

## Expected result

- A valid command like `1011` returns HTTP 200 with success true.
- An invalid command like `1012` returns HTTP 400 with `INVALID_COMMAND`.
- The validation layer rejects malformed strings.

## Verification before next phase

For the local trusted-network setup, confirm:

1. The server responds on `/health`.
2. Valid command requests succeed without strict client auth.
3. Invalid commands fail with structured errors.
4. The validator rejects all invalid test cases.
5. The app is reachable from other devices on the same LAN using the machine IP, such as `http://192.168.1.10:8000`.

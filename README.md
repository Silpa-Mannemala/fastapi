# Device API

A small FastAPI modular monolith for registering and monitoring network devices. Routes handle HTTP requests, the service applies device rules, the repository stores devices and alerts in memory, and the events module records an alert when a device transitions from online to offline.

Device and alert data is shared across requests while the application is running. It resets when the process restarts; this project does not use a database.

## Setup and Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install fastapi uvicorn pydantic pytest
uvicorn app.main:app --reload
```

Open the interactive API documentation at <http://127.0.0.1:8000/docs>. The OpenAPI schema is at <http://127.0.0.1:8000/openapi.json>.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `POST` | `/devices` | Register a device; returns `201`. |
| `GET` | `/devices` | List registered devices. |
| `GET` | `/devices/{device_id}` | Get one device; returns `404` if missing. |
| `PATCH` | `/devices/{device_id}/status` | Update status; returns `404` if missing. |
| `GET` | `/alerts` | List recorded offline alerts. |
| `GET` | `/health` | Check application health. |

Device types are `router`, `switch`, and `server`. IP addresses must be IPv4. Status is `online` or `offline` and defaults to `online` when registering a device.

For example, register a device with:

```json
{
	"name": "office-router",
	"device_type": "router",
	"ip_address": "192.168.1.1"
}
```

Use the returned `device_id` to update its status with `PATCH /devices/{device_id}/status` and body `{"status":"offline"}`. An alert is recorded only on the online-to-offline transition; repeating the offline update does not add another alert. `POST /devices` documents a `409` response for duplicate IDs.

## Tests

Run the service tests from the project root:

```bash
python -m pytest -q
```

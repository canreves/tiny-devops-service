# tiny-devops-service

Tiny HTTP service for the Insider One DevOps internship case study.

This repository currently contains the Day 1 foundation: a small Python/FastAPI HTTP service with unit tests and a Docker image. Kubernetes, Helm, CI/CD, and observability will be added in later steps of the case study.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/ping` | Simple smoke check. Returns `pong`. |
| `GET` | `/healthz` | Health endpoint for probes. |
| `GET` | `/version` | Returns version and commit metadata from environment variables. |

## Requirements

- Python 3.12+ recommended
- Docker Desktop
- `make` optional, but useful for the common commands below

## Local Development

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the service locally:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

If port `8000` is already in use, choose another host port for local development:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

Verify the app:

```bash
curl http://localhost:8000/ping
curl http://localhost:8000/healthz
curl http://localhost:8000/version
```

## Tests

Run the unit tests:

```bash
python -m pytest
```

Expected result:

```text
3 passed
```

## Docker

Build the image:

```bash
docker build -t tiny-devops-service:local .
```

Run the container:

```bash
docker run --rm -p 8002:8000 tiny-devops-service:local
```

The container listens on port `8000`. The command above maps your local machine's port `8002` to the container's port `8000`.

Verify the container:

```bash
curl http://localhost:8002/ping
curl http://localhost:8002/healthz
curl http://localhost:8002/version
```

## Make Targets

Common commands are also available through `make`:

```bash
make test
make run
make build
make docker-run
```

The Makefile uses the local virtual environment by default (`./.venv/bin/python` and `./.venv/bin/uvicorn`). Create the virtual environment and install dependencies before using `make test` or `make run`.

## Environment Variables

The app reads these optional environment variables:

| Name | Default | Purpose |
| --- | --- | --- |
| `APP_VERSION` | `dev` | Human-readable application version. |
| `GIT_SHA` | `local` | Commit SHA or build identifier. |

See `.env.example` for the expected variable names.

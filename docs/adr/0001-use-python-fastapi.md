# ADR 0001: Use Python and FastAPI

## Status

Accepted

## Context

The case study needs a small HTTP service with simple health, version, and
observability endpoints. The service should be easy to test, containerize, and
deploy to Kubernetes.

## Decision

Use Python with FastAPI.

## Consequences

- FastAPI provides a small and clear HTTP surface for `/ping`, `/healthz`,
  `/version`, and `/metrics`.
- Unit tests can run quickly with `pytest` and FastAPI's test client.
- The Docker image can stay small by using a Python slim runtime image.
- Prometheus metrics can be exposed directly from the application with the
  Python Prometheus client.

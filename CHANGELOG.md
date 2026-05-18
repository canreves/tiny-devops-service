# Changelog

## v0.1.0

- Added the FastAPI HTTP service with `/ping`, `/healthz`, and `/version`.
- Added unit tests for the base endpoints.
- Added a multi-stage, non-root Docker image with a container healthcheck.
- Added local Docker Compose support and build metadata for `/version`.
- Added a Helm chart with Deployment, Service, Ingress, ConfigMap, Secret, probes, resources, and dev/prod values.
- Added GitHub Actions CI for tests, image build, secret scanning, Trivy image scanning, and GHCR publishing.

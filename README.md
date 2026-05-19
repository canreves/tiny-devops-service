# tiny-devops-service

Tiny HTTP service for the Insider One DevOps internship case study.

This repository contains a small Python/FastAPI HTTP service with tests, a Docker image, a Helm chart for minikube, GitHub Actions CI/CD, and local observability with Prometheus and Grafana.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/ping` | Simple smoke check. Returns `pong`. |
| `GET` | `/healthz` | Health endpoint for probes. |
| `GET` | `/version` | Returns version and commit metadata from environment variables. |
| `GET` | `/metrics` | Prometheus metrics endpoint. |

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
5 passed
```

## Docker

Build the image:

```bash
docker build -t tiny-devops-service:local .
```

To include the current commit in `/version`, pass build arguments:

```bash
docker build \
  --build-arg APP_VERSION=dev \
  --build-arg GIT_SHA=$(git rev-parse --short HEAD) \
  -t tiny-devops-service:local .
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

You can also use Docker Compose for local container development:

```bash
GIT_SHA=$(git rev-parse --short HEAD) docker compose up --build
```

## Make Targets

Common commands are also available through `make`:

```bash
make test
make run
make build
make docker-run
make helm-lint
make deploy-dev
make rollout-status
```

The Makefile uses the local virtual environment by default (`./.venv/bin/python` and `./.venv/bin/uvicorn`). Create the virtual environment and install dependencies before using `make test` or `make run`.

## Environment Variables

The app reads these optional environment variables:

| Name | Default | Purpose |
| --- | --- | --- |
| `APP_VERSION` | `dev` | Human-readable application version. |
| `GIT_SHA` | `local` | Commit SHA or build identifier. |

See `.env.example` for the expected variable names.

## Kubernetes and Helm

Day 2 deploys the Docker image to minikube with the Helm chart in `helm/`.

Start minikube and load the local image:

```bash
minikube start --driver=docker
make build
minikube image load tiny-devops-service:local
```

Validate and render the chart:

```bash
helm lint ./helm
helm template tiny-devops-service ./helm -f ./helm/values-dev.yaml
```

Deploy the dev environment:

```bash
helm upgrade --install tiny-devops-service ./helm -f ./helm/values-dev.yaml
kubectl rollout status deployment/tiny-devops-service
kubectl get pods
```

Test through the Service:

```bash
kubectl port-forward service/tiny-devops-service 8080:80
curl http://localhost:8080/ping
```

Exercise a rollout and rollback:

```bash
docker tag tiny-devops-service:local tiny-devops-service:rollout-test
minikube image load tiny-devops-service:rollout-test
helm upgrade tiny-devops-service ./helm -f ./helm/values-dev.yaml --set image.tag=rollout-test
kubectl rollout status deployment/tiny-devops-service
helm history tiny-devops-service
helm rollback tiny-devops-service 1
kubectl rollout status deployment/tiny-devops-service
```

The dev and prod values files intentionally differ in replica count, ingress host, log level, and resource requests/limits.

## Observability

Day 4 adds request correlation, structured logs, Prometheus metrics, a ServiceMonitor, a PrometheusRule, and a Grafana dashboard.

Application behavior:

- every response includes `X-Request-ID`
- incoming `X-Request-ID` values are preserved for request correlation
- completed HTTP requests are logged as JSON
- `/metrics` exposes request counters and latency histograms

Install the local monitoring stack:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

Enable chart-managed monitoring resources:

```bash
helm upgrade --install tiny-devops-service ./helm \
  -f ./helm/values-dev.yaml \
  --set serviceMonitor.enabled=true \
  --set prometheusRule.enabled=true
```

Provision the Grafana dashboard from the repository:

```bash
kubectl create configmap tiny-devops-service-grafana-dashboard \
  -n monitoring \
  --from-file=tiny-devops-service-dashboard.json=docs/grafana/tiny-devops-service-dashboard.json \
  --dry-run=client \
  -o yaml | kubectl apply -f -

kubectl label configmap -n monitoring tiny-devops-service-grafana-dashboard \
  grafana_dashboard=1 \
  --overwrite
```

See `RUNBOOK.md` for verification, PromQL queries, Grafana access, and rollback steps.

## CI/CD and Supply Chain

Day 3 uses GitHub Actions to validate the service and publish images to GitHub Container Registry.

The CI workflow runs on pull requests, pushes to `main`, and version tags:

```text
.github/workflows/ci.yml
```

It performs these checks:

- scans the repository with Gitleaks for committed secrets
- installs Python dependencies
- checks Python syntax with `compileall`
- runs unit tests with `pytest`
- builds a local Docker image
- scans the image with Trivy and fails on fixed HIGH or CRITICAL vulnerabilities
- pushes successful `main` images to GHCR

Images are published under:

```text
ghcr.io/canreves/tiny-devops-service
```

The workflow uses the built-in `GITHUB_TOKEN` for GHCR authentication. No long-lived registry token is required.

Create a version tag and GitHub Release:

```bash
git tag v0.1.0
git push origin v0.1.0
```

Pushing a `v*` tag runs `.github/workflows/release.yml`, which creates the GitHub Release from `CHANGELOG.md` if it does not already exist.

For Track B, CI does not deploy directly to local minikube because GitHub-hosted runners cannot reach a laptop cluster. The deploy handoff is the pushed GHCR image; a local minikube update can be done with Helm:

```bash
helm upgrade tiny-devops-service ./helm \
  -f ./helm/values-dev.yaml \
  --set image.repository=ghcr.io/canreves/tiny-devops-service \
  --set image.tag=sha-<commit-sha>
```

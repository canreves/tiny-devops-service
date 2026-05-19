# Architecture

`tiny-devops-service` is a small FastAPI application packaged as a Docker image
and deployed to minikube with Helm.

```mermaid
flowchart LR
    Dev[Developer] --> Git[GitHub Repository]
    Git --> CI[GitHub Actions CI]
    CI --> GHCR[GitHub Container Registry]

    Dev --> Docker[Local Docker Image]
    Docker --> Minikube[Minikube Image Cache]
    Minikube --> Helm[Helm Release]
    Helm --> Deployment[Kubernetes Deployment]
    Deployment --> Pod[FastAPI Pod]
    Service[Kubernetes Service] --> Pod

    Pod --> Logs[JSON Logs]
    Pod --> Metrics[/metrics]
    Metrics --> Prometheus[Prometheus]
    Prometheus --> Grafana[Grafana Dashboard]
    Prometheus --> Alert[PrometheusRule]
```

## Runtime Flow

1. A client calls the Kubernetes Service.
2. The Service routes traffic to the FastAPI pod on port `8000`.
3. Middleware records a JSON access log and updates Prometheus counters and
   latency histograms.
4. Prometheus scrapes `/metrics` through the ServiceMonitor.
5. Grafana reads Prometheus data and renders the service dashboard.

## Release Flow

1. GitHub Actions validates the repository with secret scanning, Python checks,
   tests, Docker build, and Trivy image scanning.
2. Successful `main` builds publish an image to GHCR.
3. Local minikube deployments use Helm to select either the local image or a
   GHCR image tag.

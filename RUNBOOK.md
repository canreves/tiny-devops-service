# Runbook

Operational notes for running `tiny-devops-service` locally and on minikube.

## Local Health Check

Run the service:

```bash
make run
```

Verify the public endpoints:

```bash
curl http://localhost:8000/ping
curl http://localhost:8000/healthz
curl http://localhost:8000/version
curl http://localhost:8000/metrics
```

Each HTTP response includes an `X-Request-ID` header. If the request already
has `X-Request-ID`, the service keeps it; otherwise it generates a new UUID.

## Build and Deploy to Minikube

Build the image with the current commit SHA:

```bash
make build
minikube image load tiny-devops-service:local
```

Deploy the Helm chart:

```bash
make helm-lint
make deploy-dev
make rollout-status
```

Smoke test the service through Kubernetes:

```bash
kubectl port-forward service/tiny-devops-service 8080:80
curl -H "X-Request-ID: runbook-smoke-test" http://localhost:8080/ping
curl http://localhost:8080/metrics
```

Expected result:

- `/ping` returns `pong`
- the response includes `x-request-id`
- `/metrics` exposes `http_requests_total` and `http_request_duration_seconds`

## Logs

Read the application logs:

```bash
kubectl logs deployment/tiny-devops-service --tail=50
```

The application emits JSON logs for completed HTTP requests. Useful fields:

- `request_id`: correlation ID from `X-Request-ID`
- `method`: HTTP method
- `path`: request path
- `status_code`: response status
- `duration_ms`: request duration in milliseconds

Example investigation:

```bash
kubectl logs deployment/tiny-devops-service --tail=100 | rg runbook-smoke-test
```

## Prometheus

Install the local monitoring stack:

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
helm upgrade --install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

Enable the application's ServiceMonitor and alert rule:

```bash
helm upgrade --install tiny-devops-service ./helm \
  -f ./helm/values-dev.yaml \
  --set serviceMonitor.enabled=true \
  --set prometheusRule.enabled=true
```

Verify that Prometheus sees the application target:

```bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
curl http://localhost:9090/api/v1/targets
```

Expected target:

```text
job=tiny-devops-service health=up
```

Useful PromQL queries:

```promql
sum(rate(http_requests_total{job="tiny-devops-service"}[5m]))
histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{job="tiny-devops-service"}[5m])) by (le))
sum(rate(http_requests_total{job="tiny-devops-service",status_code=~"5.."}[5m]))
```

## Grafana

The dashboard definition lives at:

```text
docs/grafana/tiny-devops-service-dashboard.json
```

Create or refresh the dashboard ConfigMap:

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

Open Grafana:

```bash
kubectl port-forward -n monitoring svc/monitoring-grafana 3000:80
```

Then browse to:

```text
http://localhost:3000/d/tiny-devops-service/tiny-devops-service
```

Read the admin password from the Kubernetes secret when needed:

```bash
kubectl get secret -n monitoring monitoring-grafana \
  -o jsonpath='{.data.admin-password}' | base64 --decode
```

## Rollback

Review release history:

```bash
helm history tiny-devops-service
```

Rollback to a previous revision:

```bash
helm rollback tiny-devops-service <revision>
kubectl rollout status deployment/tiny-devops-service
```

After rollback, verify:

```bash
curl http://localhost:8080/ping
kubectl logs deployment/tiny-devops-service --tail=50
```

## Common Issues

If pods do not update after rebuilding `tiny-devops-service:local`, force a
rollout because the tag name did not change:

```bash
kubectl rollout restart deployment/tiny-devops-service
kubectl rollout status deployment/tiny-devops-service
```

If Prometheus does not discover the ServiceMonitor, check selector labels:

```bash
kubectl get prometheus -n monitoring -o yaml | rg "serviceMonitorSelector|ruleSelector|release"
kubectl get servicemonitor,prometheusrule --show-labels
```

The local kube-prometheus-stack release selects monitoring resources with:

```text
release=monitoring
```

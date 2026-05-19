# ADR 0004: Use Prometheus and Grafana for Observability

## Status

Accepted

## Context

Day 4 requires logs, metrics, dashboards, and basic alerting. The service runs on
Kubernetes, so the observability stack should work naturally with Kubernetes
service discovery.

## Decision

Use `kube-prometheus-stack` for local Prometheus, Alertmanager, and Grafana.
Expose application metrics at `/metrics`, add a Helm-managed ServiceMonitor and
PrometheusRule, and store the Grafana dashboard JSON in the repository.

## Consequences

- Prometheus discovers the application through ServiceMonitor instead of manual
  scrape configuration.
- Grafana can provision the dashboard from a labeled ConfigMap.
- The alert rule is versioned with the Helm chart.
- The local monitoring stack uses the `release=monitoring` selector label, so
  chart resources include that label by default.

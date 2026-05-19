# ADR 0002: Use Helm for Kubernetes Manifests

## Status

Accepted

## Context

The service needs repeatable Kubernetes deployment with environment-specific
configuration. Day 2 also requires rollout and rollback workflows.

## Decision

Use a local Helm chart under `helm/`.

## Consequences

- `values-dev.yaml` and `values-prod.yaml` can express environment differences
  without duplicating manifests.
- `helm upgrade --install` provides repeatable deploys.
- `helm history` and `helm rollback` provide a simple rollback path.
- Optional observability resources such as ServiceMonitor and PrometheusRule can
  be controlled through chart values.

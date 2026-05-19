# ADR 0003: Use Local Minikube for Track B Deployment

## Status

Accepted

## Context

The case study Track B uses local Kubernetes. GitHub-hosted runners cannot
directly reach a developer laptop's minikube cluster, so CI cannot safely deploy
to that cluster.

## Decision

Use GitHub Actions for validation and image publishing, then use local Helm
commands to deploy the selected image to minikube.

## Consequences

- CI remains useful for tests, image builds, vulnerability scans, and GHCR image
  publishing.
- Local deployment remains explicit and auditable through Helm commands.
- The deploy handoff is the container image tag, for example
  `ghcr.io/canreves/tiny-devops-service:sha-<commit-sha>`.

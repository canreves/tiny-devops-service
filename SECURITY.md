# Security

## Secrets

Do not commit real credentials, tokens, private keys, or `.env` files. Runtime values should be supplied through local environment variables, GitHub Actions secrets, or Kubernetes Secrets.

The repository includes `.env.example` only as documentation for expected variable names.

## CI Supply Chain Checks

The Day 3 CI workflow includes:

- Gitleaks repository scanning for committed secrets.
- Docker image vulnerability scanning with Trivy.
- GHCR publishing through GitHub's short-lived `GITHUB_TOKEN`.

Trivy is configured to fail the pipeline when fixed HIGH or CRITICAL vulnerabilities are found. The Trivy GitHub Action is pinned to an explicit release tag instead of a floating `latest` reference.

## Token Handling

The workflow does not use long-lived registry credentials. GHCR authentication uses the repository-scoped `GITHUB_TOKEN` with `packages: write` permission only for push/tag events.

If a real secret is ever exposed, rotate it immediately and treat the Git history as compromised until reviewed.

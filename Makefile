PYTHON ?= ./.venv/bin/python
UVICORN ?= ./.venv/bin/uvicorn
APP_VERSION ?= dev
GIT_SHA ?= $(shell git rev-parse --short HEAD)

.PHONY: test run build docker-run helm-lint helm-template deploy-dev rollout-status dashboard-configmap

test:
	$(PYTHON) -m pytest

run:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

build:
	docker build \
		--build-arg APP_VERSION=$(APP_VERSION) \
		--build-arg GIT_SHA=$(GIT_SHA) \
		-t tiny-devops-service:local .

docker-run:
	docker run --rm -p 8002:8000 tiny-devops-service:local

helm-lint:
	helm lint ./helm

helm-template:
	helm template tiny-devops-service ./helm -f ./helm/values-dev.yaml

deploy-dev:
	helm upgrade --install tiny-devops-service ./helm -f ./helm/values-dev.yaml

rollout-status:
	kubectl rollout status deployment/tiny-devops-service

dashboard-configmap:
	kubectl create configmap tiny-devops-service-grafana-dashboard \
		-n monitoring \
		--from-file=tiny-devops-service-dashboard.json=docs/grafana/tiny-devops-service-dashboard.json \
		--dry-run=client \
		-o yaml | kubectl apply -f -
	kubectl label configmap -n monitoring tiny-devops-service-grafana-dashboard grafana_dashboard=1 --overwrite

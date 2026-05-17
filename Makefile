PYTHON ?= ./.venv/bin/python
UVICORN ?= ./.venv/bin/uvicorn
APP_VERSION ?= dev
GIT_SHA ?= $(shell git rev-parse --short HEAD)

.PHONY: test run build docker-run

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

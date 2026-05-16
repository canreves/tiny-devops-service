PYTHON ?= ./.venv/bin/python
UVICORN ?= ./.venv/bin/uvicorn

.PHONY: test run build docker-run

test:
	$(PYTHON) -m pytest

run:
	$(UVICORN) app.main:app --host 0.0.0.0 --port 8000

build:
	docker build -t tiny-devops-service:local .

docker-run:
	docker run --rm -p 8002:8000 tiny-devops-service:local

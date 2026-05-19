from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from prometheus_client.registry import CollectorRegistry

registry = CollectorRegistry()

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests.",
    ("method", "path", "status_code"),
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds.",
    ("method", "path", "status_code"),
    registry=registry,
)


def record_request(method: str, path: str, status_code: int, duration_seconds: float) -> None:
    labels = (method, path, str(status_code))
    REQUEST_COUNT.labels(*labels).inc()
    REQUEST_LATENCY.labels(*labels).observe(duration_seconds)


def render_metrics() -> bytes:
    return generate_latest(registry)

import os 
import logging
import time
import uuid
from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import PlainTextResponse, Response

from app.logging_config import configure_logging
from app.metrics import CONTENT_TYPE_LATEST, record_request, render_metrics

configure_logging()
app = FastAPI(title="tiny-devops-service")
logger = logging.getLogger("tiny-devops-service")


@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start_time = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        duration_seconds = time.perf_counter() - start_time
        path = request.url.path
        record_request(request.method, path, status_code, duration_seconds)

        logger.info(
            "request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": path,
                "status_code": status_code,
                "duration_ms": round(duration_seconds * 1000, 3),
            },
        )

        if "response" in locals():
            response.headers["X-Request-ID"] = request_id

@app.get("/ping", response_class=PlainTextResponse)
def ping() -> str: 
    return "pong"

@app.get("/healthz")
def healthz() -> dict[str,str]: 
    return {"status": "ok"} 

@app.get("/version")
def version() -> dict[str, str]:
    return {
        "version": os.getenv("APP_VERSION", "dev"),
        "commit": os.getenv("GIT_SHA", "local")
    }

@app.get("/metrics")
def metrics() -> Response:
    return Response(content=render_metrics(), media_type=CONTENT_TYPE_LATEST)

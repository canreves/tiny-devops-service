import os 
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse

app = FastAPI(title="tiny-devops-service")

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
    
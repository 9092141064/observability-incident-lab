import json
import os
import time
import uuid
from datetime import datetime, timezone

import redis
from fastapi import FastAPI, HTTPException, Query, Response

app = FastAPI(title="Observability Sample App")

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=1.0)


def log_json(level: str, endpoint: str, status_code: int, latency_ms: float, error: str | None = None):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "level": level,
        "endpoint": endpoint,
        "status_code": status_code,
        "latency_ms": round(latency_ms, 2),
        "error": error,
    }
    print(json.dumps(payload), flush=True)


@app.get("/health")
def health(response: Response):
    start = time.perf_counter()
    try:
        r.ping()
        latency = (time.perf_counter() - start) * 1000
        log_json("INFO", "/health", 200, latency)
        return {"status": "ok", "redis": "reachable"}
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        response.status_code = 503
        log_json("ERROR", "/health", 503, latency, error=str(exc))
        return {"status": "degraded", "redis": "unreachable", "error": str(exc)}


@app.post("/items")
def create_item(name: str = Query(default="sample-item")):
    start = time.perf_counter()
    try:
        item_id = str(uuid.uuid4())[:8]
        r.hset(f"item:{item_id}", mapping={"id": item_id, "name": name})
        latency = (time.perf_counter() - start) * 1000
        log_json("INFO", "/items", 201, latency)
        return {"id": item_id, "name": name}
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        log_json("ERROR", "/items", 500, latency, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@app.get("/items/{item_id}")
def get_item(item_id: str):
    start = time.perf_counter()
    try:
        data = r.hgetall(f"item:{item_id}")
        latency = (time.perf_counter() - start) * 1000
        if not data:
            log_json("WARN", f"/items/{item_id}", 404, latency, error="Not found")
            raise HTTPException(status_code=404, detail="Item not found")
        log_json("INFO", f"/items/{item_id}", 200, latency)
        return data
    except HTTPException:
        raise
    except Exception as exc:
        latency = (time.perf_counter() - start) * 1000
        log_json("ERROR", f"/items/{item_id}", 500, latency, error=str(exc))
        raise HTTPException(status_code=500, detail=f"Database error: {exc}")


@app.get("/slow")
def slow_endpoint(delay_seconds: float = Query(default=1.5, ge=0.1, le=10.0)):
    start = time.perf_counter()
    time.sleep(delay_seconds)
    latency = (time.perf_counter() - start) * 1000
    log_json("WARN", "/slow", 200, latency, error="Simulated artificial latency")
    return {"status": "slow_response", "slept_seconds": delay_seconds}


@app.get("/simulate-error")
def simulate_error():
    start = time.perf_counter()
    latency = (time.perf_counter() - start) * 1000
    log_json("ERROR", "/simulate-error", 500, latency, error="Simulated application error")
    raise HTTPException(status_code=500, detail="Simulated failure triggered")

from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, make_asgi_app
import time
import os

# Prometheus metrics
TASK_COUNT = Counter("hfog_tasks_total", "Total tasks", ["node_type", "status"])
TASK_LATENCY = Histogram("hfog_task_latency_seconds", "Task latency", ["node_type"])

app = FastAPI()

# Expose /metrics endpoint
app.mount("/metrics", make_asgi_app())

@app.post("/execute_task")
async def execute_task(request: Request):
    data = await request.json()
    task_type = data["task_type"]
    data_frequency = data["data_frequency"]
    node_type = os.environ.get("NODE_TYPE", "unknown")

    # Start latency timer
    start = time.time()

    # Simulate execution delay
    if node_type == "edge":
        time.sleep(0.001)
    elif node_type == "fog":
        time.sleep(0.005)
    elif node_type == "cloud":
        time.sleep(0.1)

    # Record elapsed time
    elapsed = time.time() - start

    # Validate execution rules
    if task_type == "sensitive" and node_type != "edge":
        TASK_COUNT.labels(node_type, "error").inc()
        TASK_LATENCY.labels(node_type).observe(elapsed)
        return {"status": "error", "message": "Sensitive tasks must execute on Edge nodes"}

    if data_frequency == "high" and node_type == "cloud":
        TASK_COUNT.labels(node_type, "error").inc()
        TASK_LATENCY.labels(node_type).observe(elapsed)
        return {"status": "error", "message": "High-frequency data should stay in Edge/Fog"}

    # Success path
    TASK_COUNT.labels(node_type, "success").inc()
    TASK_LATENCY.labels(node_type).observe(elapsed)
    return {"status": "success", "message": f"Task executed on {node_type}"}

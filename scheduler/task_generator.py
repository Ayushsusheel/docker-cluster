import time
import random
import requests

TASK_TYPES = ["sensitive", "non-sensitive"]
FREQ_TYPES = ["high", "low"]

# Use host.docker.internal to talk back to your host machine's exposed ports
NODES = {
    "edge": [
        f"http://host.docker.internal:{8001 + i}/execute_task"
        for i in range(15)
    ],
    "fog": [
        f"http://host.docker.internal:{8101 + i}/execute_task"
        for i in range(10)
    ],
    "cloud": ["http://host.docker.internal:9001/execute_task"]
}

def generate_task():
    return {
        "task_type": random.choice(TASK_TYPES),
        "data_frequency": random.choice(FREQ_TYPES)
    }

def choose_node(task):
    if task["task_type"] == "sensitive":
        return "edge", NODES["edge"]
    elif task["data_frequency"] == "high":
        return "fog", NODES["fog"]
    else:
        return "cloud", NODES["cloud"]

def send_task(task, node_type, urls):
    for url in urls:
        try:
            response = requests.post(
                url,
                json={**task, "node_type": node_type},
                timeout=2
            )
            print(f"Task: {task}, Sent to: {url} -> Response: {response.json()}")
            return
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Failed to send to {url} ({node_type}): {e}")
    print(f"❌ All {node_type} nodes failed for task: {task}")

if __name__ == "__main__":
    while True:
        task = generate_task()
        node_type, node_urls = choose_node(task)
        send_task(task, node_type, node_urls)
        time.sleep(5)

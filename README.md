Project Lab Draft: Edge-Fog-Cloud Cluster using Docker 
Containers and Kubernetes 
Objective 
To implement a edge fog cloud Continuum where tasks are scheduled and executed based 
on: 
1. Security Sensitivity: 
○ Security-sensitive tasks execute only on Edge nodes. 
○ Non-sensitive tasks can execute on Edge, Fog, or Cloud nodes. 
2. Data Access Frequency: 
○ Frequently accessed data is stored on Edge/Fog nodes. 
○ Less frequently accessed data is stored on the Cloud. 
3. Communication Delays: 
○ Edge Nodes: ~1 ms. 
○ Fog Nodes: ~5 ms. 
○ Cloud: ~100 ms. 
System Architecture 
● 15 Edge Nodes (Low latency, close to users) 
● 10 Fog Nodes (Intermediate processing layer) 
● 1 Cloud Data Center (High latency, large storage, high computing power) 
● Task Controller (Implemented using FastAPI, deployed on each node) 
● Task Scheduler (Decides job execution location based on security and data constraints) 
Tools & Technologies 
● Docker (Containerization of Edge, Fog, and Cloud nodes) 
● Kubernetes (Orchestration of containerized nodes) 
● FastAPI (Microservices for task execution decisions) 
● Python (Simulation of task generation and scheduling) 
Implementation Steps 
Step 1: Set Up the Kubernetes Cluster 
1. Create a Kubernetes cluster with 26 nodes: 
○ 15 Edge nodes (edge-1 to edge-15) 
○ 10 Fog nodes (fog-1 to fog-10) 
○ 1 Cloud node (cloud) 
Assign labels to nodes: 
 kubectl label nodes edge-1 type=edge 
kubectl label nodes fog-1 type=fog 
kubectl label nodes cloud type=cloud 
Step 2: Deploy FastAPI-based Task Controllers 
1. Create a FastAPI microservice to handle task execution based on constraints. 
2. Deploy it as a Kubernetes Deployment on each node. 
Example FastAPI Controller Code (Runs on each node): 
from fastapi import FastAPI, Request 
 
app = FastAPI() 
 
@app.post("/execute_task") 
async def execute_task(request: Request): 
    data = await request.json() 
    task_type = data["task_type"]  # "sensitive" or "non-sensitive" 
    data_frequency = data["data_frequency"]  # "high" or "low" 
 
    node_type = data["node_type"]  # "edge", "fog", "cloud" 
 
    # Define execution rules 
    if task_type == "sensitive" and node_type != "edge": 
        return {"status": "error", "message": "Sensitive tasks must execute on Edge nodes"} 
 
    if data_frequency == "high" and node_type == "cloud": 
        return {"status": "error", "message": "High-frequency data should stay in Edge/Fog"} 
 
    return {"status": "success", "message": f"Task executed on {node_type}"} 
 
Step 3: Task Scheduling Logic 
1. Implement a scheduler to decide where tasks should run. 
2. The scheduler should consider: 
○ Security constraint: Sensitive tasks → Edge only 
○ Data constraint: High-frequency data → Edge/Fog 
Example Scheduler Code: 
import requests 
 
TASKS = [ 
    {"task_type": "sensitive", "data_frequency": "high"}, 
    {"task_type": "non-sensitive", "data_frequency": "low"}, 
    {"task_type": "sensitive", "data_frequency": "low"}, 
    {"task_type": "non-sensitive", "data_frequency": "high"}, 
] 
 
NODES = { 
    "edge": ["http://edge-1/execute_task", "http://edge-2/execute_task"], 
    "fog": ["http://fog-1/execute_task", "http://fog-2/execute_task"], 
    "cloud": ["http://cloud/execute_task"], 
} 
 
for task in TASKS: 
    if task["task_type"] == "sensitive": 
        node_url = NODES["edge"][0]  # Select an edge node 
    elif task["data_frequency"] == "high": 
        node_url = NODES["fog"][0]  # Select a fog node 
    else: 
        node_url = NODES["cloud"][0]  # Select the cloud node 
 
    response = requests.post(node_url, json={**task, "node_type": node_url.split("/")[-1]}) 
    print(response.json()) 
 
Step 4: Deploy the Task Scheduler 
● The scheduler runs as a CronJob in Kubernetes. 
● It dynamically assigns jobs based on security and data constraints. 
apiVersion: batch/v1 
kind: CronJob 
metadata: 
  name: task-scheduler 
spec: 
  schedule: "*/5 * * * *"  # Run every 5 minutes 
  jobTemplate: 
    spec: 
      template: 
        spec: 
          containers: 
- name: scheduler 
image: my-scheduler-image  # Build the scheduler into a Docker container 
restartPolicy: OnFailure 
Step 5: Monitor Job Execution 
● Use kubectl logs to track task execution. 
kubectl logs -f deployment/task-scheduler 
● Use Prometheus + Grafana for real-time monitoring. 
Expected Outcome 
● Security-sensitive tasks execute only on Edge nodes. 
● High-frequency data tasks execute on Edge/Fog nodes. 
● Non-sensitive tasks with low data access execute on the Cloud. 
● Execution delays reflect the real-world HFog continuum: 
○ Edge: ~1 ms 
○ Fog: ~5 ms 
○ Cloud: ~100 ms 
Optional: 
● Load balancing: Optimize task distribution across Edge/Fog nodes. 
● Resource-aware scheduling: Consider CPU/memory constraints before assigning jobs. 
● Dynamic scaling: Scale Edge/Fog nodes based on workload demand.

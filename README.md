<br/><br/>
**Explaination:- https://youtu.be/jPNRJDdI1Cw**
   
<br/>
<br/><br/>
Project Lab Draft: Edge-Fog-Cloud Cluster using Docker 
Containers and Kubernetes 
Objective 
To implement a edge fog cloud Continuum where tasks are scheduled and executed based 
on: 
1. Security Sensitivity: 
<br/>○ Security-sensitive tasks execute only on Edge nodes. 
<br/>○ Non-sensitive tasks can execute on Edge, Fog, or Cloud nodes. 

<br/>
2. Data Access Frequency: 
<br/>○ Frequently accessed data is stored on Edge/Fog nodes. 
<br/>○ Less frequently accessed data is stored on the Cloud. 
<br/>3. Communication Delays: 
<br/>○ Edge Nodes: ~1 ms. 
<br/>○ Fog Nodes: ~5 ms. 
<br/>○ Cloud: ~100 ms. 
<br/>System Architecture 
<br/>● 15 Edge Nodes (Low latency, close to users) 
<br/>● 10 Fog Nodes (Intermediate processing layer) 
<br/>● 1 Cloud Data Center (High latency, large storage, high computing power) 
<br/>● Task Controller (Implemented using FastAPI, deployed on each node) 
<br/>● Task Scheduler (Decides job execution location based on security and data constraints) 
<br/>Tools & Technologies 
<br/>● Docker (Containerization of Edge, Fog, and Cloud nodes) 
<br/>● Kubernetes (Orchestration of containerized nodes) 
<br/>● FastAPI (Microservices for task execution decisions) 
<br/>● Python (Simulation of task generation and scheduling) 
<br/>Implementation Steps 
<br/>Step 1: Set Up the Kubernetes Cluster 
<br/>1. Create a Kubernetes cluster with 26 nodes: 
<br/>○ 15 Edge nodes (edge-1 to edge-15) 
<br/>○ 10 Fog nodes (fog-1 to fog-10) 
<br/>○ 1 Cloud node (cloud) 
<br/><br/>Assign labels to nodes: 
 <br/>kubectl label nodes edge-1 type=edge 
<br/>kubectl label nodes fog-1 type=fog 
<br/>kubectl label nodes cloud type=cloud 
<br/>Step 2: Deploy FastAPI-based Task Controllers 
<br/>1. Create a FastAPI microservice to handle task execution based on constraints. 
<br/>2. Deploy it as a Kubernetes Deployment on each node. 
<br/>Example FastAPI Controller Code (Runs on each node): 
<br/>from fastapi import FastAPI, Request 
 
<br/>app = FastAPI() 
 
<br/>@app.post("/execute_task") 
<br/>async def execute_task(request: Request): 
    <br/>data = await request.json() 
    <br/>task_type = data["task_type"]  # "sensitive" or "non-sensitive" 
    <br/>data_frequency = data["data_frequency"]  # "high" or "low" 
 
    <br/>node_type = data["node_type"]  # "edge", "fog", "cloud" 
 
    <br/># Define execution rules 
    <br/>if task_type == "sensitive" and node_type != "edge": 
       <br/> return {"status": "error", "message": "Sensitive tasks must execute on Edge nodes"} 
 
    if data_frequency == "high" and node_type == "cloud": 
        return {"status": "error", "message": "High-frequency data should stay in Edge/Fog"} 
 
    return {"status": "success", "message": f"Task executed on {node_type}"} 
 
<br/>Step 3: Task Scheduling Logic 
<br/>1. Implement a scheduler to decide where tasks should run. 
<br/>2. The scheduler should consider: 
<br/>○ Security constraint: Sensitive tasks → Edge only 
<br/>○ Data constraint: High-frequency data → Edge/Fog 
<br/>Example Scheduler Code: 
<br/>import requests 
<br/> 
TASKS = [ 
    {"task_type": "sensitive", "data_frequency": "high"}, 
    {"task_type": "non-sensitive", "data_frequency": "low"}, 
    {"task_type": "sensitive", "data_frequency": "low"}, 
    {"task_type": "non-sensitive", "data_frequency": "high"}, 
] 
 <br/>
NODES = { 
    "edge": ["http://edge-1/execute_task", "http://edge-2/execute_task"], 
    "fog": ["http://fog-1/execute_task", "http://fog-2/execute_task"], 
    "cloud": ["http://cloud/execute_task"], 
} 
 <br/>
for task in TASKS: 
    if task["task_type"] == "sensitive": 
        node_url = NODES["edge"][0]  # Select an edge node 
    elif task["data_frequency"] == "high": 
        node_url = NODES["fog"][0]  # Select a fog node 
    else: 
        node_url = NODES["cloud"][0]  # Select the cloud node 
 
    response = requests.post(node_url, json={**task, "node_type": node_url.split("/")[-1]}) 
    print(response.json()) 
 <br/><br/>
Step 4: Deploy the Task Scheduler 
<br/>● The scheduler runs as a CronJob in Kubernetes. 
<br/>● It dynamically assigns jobs based on security and data constraints. 
<br/>apiVersion: batch/v1 
<br/>kind: CronJob 
<br/>metadata: 
  <br/>name: task-scheduler 
<br/>spec: 
  schedule: "*/5 * * * *"  # Run every 5 minutes 
  jobTemplate: 
    spec: 
      template: 
        spec: 
          containers: 
- name: scheduler 
image: my-scheduler-image  # Build the scheduler into a Docker container 
restartPolicy: OnFailure 
<br/><br/>Step 5: Monitor Job Execution 
<br/>● Use kubectl logs to track task execution. 
<br/>kubectl logs -f deployment/task-scheduler 
<br/>● Use Prometheus + Grafana for real-time monitoring. 
<br/>Expected Outcome 
<br/>● Security-sensitive tasks execute only on Edge nodes. 
<br/>● High-frequency data tasks execute on Edge/Fog nodes. 
<br/>● Non-sensitive tasks with low data access execute on the Cloud. 
<br/>● Execution delays reflect the real-world HFog continuum: 
<br/>○ Edge: ~1 ms 
<br/>○ Fog: ~5 ms 
<br/>○ Cloud: ~100 ms 
<br/>Optional: 
<br/>● Load balancing: Optimize task distribution across Edge/Fog nodes. 
<br/>● Resource-aware scheduling: Consider CPU/memory constraints before assigning jobs. 
<br/>● Dynamic scaling: Scale Edge/Fog nodes based on workload demand.

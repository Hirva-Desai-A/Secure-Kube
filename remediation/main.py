from fastapi import FastAPI, Request, HTTPException
from kubernetes import client, config
import logging
import json
import re
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("securekube-remediation")

app = FastAPI(title="SecureKube Remediation Engine")

try:
    config.load_incluster_config()
    logger.info("Loaded in-cluster Kubernetes config")
except:
    config.load_kube_config(context="kind-securekube")
    logger.info("Loaded local Kubernetes config")

v1 = client.CoreV1Api()
incident_log = []

def extract_container_name(alert_output: str) -> str:
    match = re.search(r'container=([^\s)]+)', alert_output)
    return match.group(1) if match else None

def find_pod_by_container(container_name: str, namespace: str = "securekube-app") -> str:
    pods = v1.list_namespaced_pod(namespace=namespace)
    for pod in pods.items:
        for container in pod.spec.containers:
            if container.name == container_name or container_name in pod.metadata.name:
                return pod.metadata.name
    return None

def delete_pod(pod_name: str, namespace: str = "securekube-app"):
    try:
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        logger.info(f"REMEDIATION: Deleted compromised pod {pod_name} in {namespace}")
        return True
    except client.exceptions.ApiException as e:
        logger.error(f"Failed to delete pod {pod_name}: {e}")
        return False

@app.get("/")
def root():
    return {"service": "securekube-remediation", "status": "active", "incidents": len(incident_log)}

@app.get("/incidents")
def get_incidents():
    return {"total": len(incident_log), "incidents": incident_log}

@app.post("/webhook/falco")
async def handle_falco_alert(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    priority = body.get("priority", "").upper()
    rule = body.get("rule", "")
    output = body.get("output", "")
    
    logger.warning(f"ALERT RECEIVED | Priority: {priority} | Rule: {rule}")
    logger.warning(f"Output: {output}")

    incident = {
        "timestamp": datetime.utcnow().isoformat(),
        "priority": priority,
        "rule": rule,
        "output": output,
        "action_taken": "none"
    }

    # Auto-remediate high/critical alerts (including our Notice level shell test)
    if priority in ["CRITICAL", "NOTICE", "WARNING"]:
        container_name = extract_container_name(output)
        pod_name = None
        
        if "k8s_pod_name=" in output:
            match = re.search(r'k8s_pod_name=([^\s]+)', output)
            if match:
                pod_name = match.group(1)

        if not pod_name and container_name:
            pod_name = find_pod_by_container(container_name)

        if pod_name:
            success = delete_pod(pod_name)
            incident["action_taken"] = f"pod_deleted:{pod_name}" if success else "deletion_failed"
            logger.critical(f"AUTO-REMEDIATION: Pod {pod_name} deleted due to rule '{rule}'")
        else:
            incident["action_taken"] = "pod_not_found"
            logger.warning("Could not find pod to terminate.")
    else:
        incident["action_taken"] = "logged_only"

    incident_log.append(incident)
    return {"status": "processed", "incident": incident}

@app.get("/health")
def health():
    return {"status": "healthy"}
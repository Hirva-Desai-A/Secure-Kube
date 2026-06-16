from fastapi import FastAPI, Request
from kubernetes import client, config
import logging
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("securekube-remediation")

app = FastAPI(title="SecureKube Remediation Engine")

try:
    config.load_incluster_config()
except:
    config.load_kube_config(context="kind-securekube")

v1 = client.CoreV1Api()

def find_pod_by_container_id(container_id: str, namespace: str = "securekube-app"):
    try:
        pods = v1.list_namespaced_pod(namespace=namespace)
        for pod in pods.items:
            if pod.status.container_statuses:
                for status in pod.status.container_statuses:
                    if status.container_id and container_id in status.container_id:
                        return pod.metadata.name
    except Exception as e:
        logger.error(f"Error finding pod: {e}")
    return None

def delete_pod(pod_name: str, namespace: str = "securekube-app"):
    try:
        v1.delete_namespaced_pod(name=pod_name, namespace=namespace)
        logger.info(f"REMEDIATION: Deleted compromised pod {pod_name}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete {pod_name}: {e}")
        return False

@app.post("/webhook/falco")
async def handle_falco_alert(request: Request):
    try:
        body = await request.json()
        output = body.get("output", "")
        
        # Log the raw alert so we can see what Falco is sending
        logger.info(f"Received Alert: {output}")

        pod_match = re.search(r'k8s\.pod\.name=([^\s,]+)', output)
        pod_name = pod_match.group(1) if pod_match else None
        
        if not pod_name or pod_name == "<NA>":
            container_id_match = re.search(r'container_id=([^\s,]+)', output)
            if container_id_match:
                pod_name = find_pod_by_container_id(container_id_match.group(1))

        if pod_name and pod_name != "<NA>":
            delete_pod(pod_name)
            return {"status": "remediated"}
        
        return {"status": "ignored"}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error"}

@app.get("/health")
def health():
    return {"status": "healthy"}
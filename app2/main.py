from fastapi import FastAPI
import uvicorn
import httpx

app = FastAPI(title="SecureKube Payment Service")

@app.get("/")
def root():
    return {"service": "payment-service", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/pay")
async def pay():
    async with httpx.AsyncClient() as client:
        try:
            # Notice how it calls the internal Kubernetes service name directly!
            resp = await client.get("http://securekube-api-svc.securekube-app.svc.cluster.local/transaction", timeout=3.0)
            return {"payment": "processed", "transaction": resp.json()}
        except Exception as e:
            return {"payment": "failed", "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

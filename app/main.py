from fastapi import FastAPI
import uvicorn

app = FastAPI(title="SecureKube FinTech API")

@app.get("/")
def root():
    return {"service": "securekube-api", "status": "running", "version": "1.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/transaction")
def transaction():
    return {"transaction_id": "TXN-001", "amount": 5000, "currency": "INR", "status": "approved"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

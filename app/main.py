from fastapi import FastAPI
import uvicorn

# Create FastAPI application
app = FastAPI(
    title="HydraSec FinTech API",
    description="A beginner DevSecOps microservice",
    version="1.0"
)

# Root endpoint
@app.get("/")
def root():
    return {
        "service": "hydrasec-api",
        "status": "running",
        "version": "1.0"
    }

# Health check endpoint
@app.get("/health")
def health():
    return {
        "status": "healthy"
    }

# Transaction endpoint
@app.get("/transaction")
def transaction():
    return {
        "transaction_id": "TXN-001",
        "amount": 5000,
        "currency": "INR",
        "status": "approved"
    }

# Run application
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
import os
import logging

from prometheus_client import Counter, Gauge
from prometheus_fastapi_instrumentator import Instrumentator
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("securekube-api")

# Database URL from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    txn_id = Column(String, unique=True, index=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="pending")

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="SecureKube API")

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/transaction")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()


from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="SecureKube API")

# 1. Define the custom metric for the Data Persistence dashboard panel
TRANSACTION_COUNTER = Counter(
    "securekube_transactions_total", 
    "Total number of database transactions processed"
)

# 2. Bind the Instrumentator to the app to automatically track API HTTP Metrics
instrumentator = Instrumentator().instrument(app)

@app.on_event("startup")
def startup_event():
    init_db()
    # 3. Expose the /metrics endpoint so Prometheus can scrape the app
    instrumentator.expose(app)

@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/transaction")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()

@app.post("/transaction")
def create_mock_transaction(amount: float = 100.0, db: Session = Depends(get_db)):
    # 4. Increment the metric whenever data is persisted!
    TRANSACTION_COUNTER.inc()
    return {"status": "success", "amount": amount}
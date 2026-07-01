import logging
import os
import time

from fastapi import Depends, FastAPI
from prometheus_client import Counter
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import Column, Float, Integer, String, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("securekube-api")

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./securekube.db")
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


def wait_for_db(max_attempts: int = 30, delay_seconds: int = 2) -> None:
    last_error = None
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            logger.info("Database connection is ready")
            return
        except OperationalError as exc:
            last_error = exc
            logger.warning("Database not ready yet (%s/%s): %s", attempt, max_attempts, exc)
            if attempt < max_attempts:
                time.sleep(delay_seconds)
    raise RuntimeError(f"Database did not become ready: {last_error}")


def init_db() -> None:
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(title="SecureKube API")
TRANSACTION_COUNTER = Counter(
    "securekube_transactions_total",
    "Total number of database transactions processed",
)
instrumentator = Instrumentator().instrument(app)


@app.on_event("startup")
def startup_event() -> None:
    init_db()
    instrumentator.expose(app)


@app.get("/health")
def health():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as exc:
        return {"status": "unhealthy", "error": str(exc)}


@app.get("/transaction")
def get_transactions(db: Session = Depends(get_db)):
    return db.query(Transaction).all()


@app.post("/transaction")
def create_mock_transaction(amount: float = 100.0, db: Session = Depends(get_db)):
    TRANSACTION_COUNTER.inc()
    return {"status": "success", "amount": amount}
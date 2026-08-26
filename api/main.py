from fastapi import FastAPI

from agent.orchestrator import run_lifeops
from agent.action_router import (
    approve_bill,
    check_bill,
    pay_bill,
)


app = FastAPI(
    title="LifeOps API",
    description="Autonomous financial operations API with deterministic payment safety.",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "name": "LifeOps",
        "status": "online",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
    }


@app.get("/bill/{bill_name}")
def get_bill(bill_name: str):
    return {
        "result": check_bill(bill_name)
    }


@app.post("/bill/{bill_name}/approve")
def approve(bill_name: str):
    return {
        "result": approve_bill(bill_name)
    }


@app.post("/bill/{bill_name}/pay")
def pay(bill_name: str):
    return {
        "result": pay_bill(bill_name)
    }


@app.post("/run")
def run():
    return {
        "result": run_lifeops()
    }
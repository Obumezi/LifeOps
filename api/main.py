import sqlite3

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from api.activity import get_activity_history
from api.bill_details import get_bill_details

from agent.orchestrator import run_lifeops
from agent.action_router import (
    approve_bill,
    check_bill,
    pay_bill,
)
from api.services import get_dashboard_data


app = FastAPI(
    title="LifeOps API",
    description=(
        "Autonomous financial operations API "
        "with deterministic payment safety."
    ),
    version="1.0.0",
)


# ============================================================
# DASHBOARD STATIC FILES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent
DASHBOARD_DIR = BASE_DIR / "dashboard"

app.mount(
    "/dashboard",
    StaticFiles(directory=DASHBOARD_DIR),
    name="dashboard",
)


@app.get("/")
def root():
    return FileResponse(DASHBOARD_DIR / "index.html")


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "LifeOps",
    }


# ============================================================
# DASHBOARD API
# ============================================================

@app.get("/api/dashboard")
def dashboard():
    return get_dashboard_data()


@app.get("/api/bills")
def bills():
    return get_dashboard_data()["bills"]


# ============================================================
# BILL API
# ============================================================

@app.get("/api/bill/{bill_name}")
def get_bill(bill_name: str):
    return {
        "result": check_bill(bill_name)
    }


@app.post("/api/bill/{bill_name}/approve")
def approve(bill_name: str):
    return {
        "result": approve_bill(bill_name)
    }


@app.post("/api/bill/{bill_name}/pay")
def pay(bill_name: str):
    return {
        "result": pay_bill(bill_name)
    }


# ============================================================
# LIFEOPS AGENT
# ============================================================

@app.post("/api/run")
def run():
    return {
        "result": run_lifeops()
    }


@app.post("/api/reset")
def reset_demo():
    db_path = BASE_DIR / "database" / "lifeops.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM agent_decisions")
    cursor.execute("DELETE FROM payment_transactions")

    cursor.execute("""
        UPDATE tasks
        SET status = 'pending'
    """)

    conn.commit()
    conn.close()

    return {
        "status": "reset",
        "message": "LifeOps demo reset successfully."
    }












# ============================================================
# LEGACY ROUTES
# ============================================================

@app.get("/bill/{bill_name}")
def get_bill_legacy(bill_name: str):
    return {
        "result": check_bill(bill_name)
    }


@app.post("/bill/{bill_name}/approve")
def approve_legacy(bill_name: str):
    return {
        "result": approve_bill(bill_name)
    }


@app.post("/bill/{bill_name}/pay")
def pay_legacy(bill_name: str):
    return {
        "result": pay_bill(bill_name)
    }

@app.get("/api/activity")
def activity():
    return {
        "activity": get_activity_history()
    }


@app.get("/api/bill/{bill_name}/details")
def bill_details(bill_name: str):

    details = get_bill_details(bill_name)

    if details is None:
        return {
            "error": f"No bill named '{bill_name}' was found."
        }

    return details
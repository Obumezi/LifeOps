import sqlite3

from fastapi.testclient import TestClient

from api.main import app


DB_PATH = "database/lifeops.db"

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_bill_status_endpoint():
    response = client.get("/bill/Internet%20Subscription")

    assert response.status_code == 200
    assert "Internet Subscription" in response.json()["result"]


def test_unknown_bill_endpoint():
    response = client.get("/bill/Unknown%20Bill")

    assert response.status_code == 200
    assert response.json()["result"].startswith("BILL_NOT_FOUND")





def test_dashboard_endpoint():
    response = client.get("/api/dashboard")

    assert response.status_code == 200

    data = response.json()

    assert "summary" in data
    assert "bills" in data

    assert data["summary"]["total_bills"] == 3

    


def test_approval_requires_needs_approval():
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        "DELETE FROM agent_decisions WHERE task_id = 1"
    )

    conn.execute(
        "UPDATE tasks SET status = 'pending' WHERE id = 1"
    )

    conn.commit()
    conn.close()

    try:
        response = client.post(
            "/bill/Electricity%20Bill/approve"
        )

        assert response.status_code == 200
        assert response.json()["result"].startswith(
            "APPROVAL_BLOCKED"
        )

    finally:
        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            """
            INSERT INTO agent_decisions
            (task_id, decision, reason)
            VALUES (?, ?, ?)
            """,
            (
                1,
                "NEEDS_APPROVAL",
                "Current amount exceeds automatic payment limit.",
            ),
        )

        conn.commit()
        conn.close()


def test_approved_bill_can_be_paid_once():
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        "DELETE FROM payment_transactions WHERE task_id = 1"
    )

    conn.execute(
        "DELETE FROM agent_decisions WHERE task_id = 1"
    )

    conn.execute(
        "UPDATE tasks SET status = 'pending' WHERE id = 1"
    )

    conn.execute(
        """
        INSERT INTO agent_decisions
        (task_id, decision, reason)
        VALUES (?, ?, ?)
        """,
        (
            1,
            "NEEDS_APPROVAL",
            "API integration test.",
        ),
    )

    conn.commit()
    conn.close()

    try:
        approval = client.post(
            "/bill/Electricity%20Bill/approve"
        )

        assert approval.status_code == 200
        assert approval.json()["result"].startswith(
            "APPROVED"
        )

        payment = client.post(
            "/bill/Electricity%20Bill/pay"
        )

        assert payment.status_code == 200
        assert payment.json()["result"].startswith(
            "PAYMENT_COMPLETED"
        )

        duplicate = client.post(
            "/bill/Electricity%20Bill/pay"
        )

        assert duplicate.status_code == 200
        assert duplicate.json()["result"].startswith(
            "PAYMENT_BLOCKED"
        )

        conn = sqlite3.connect(DB_PATH)

        count = conn.execute(
            """
            SELECT COUNT(*)
            FROM payment_transactions
            WHERE task_id = 1
            """
        ).fetchone()[0]

        status = conn.execute(
            """
            SELECT status
            FROM tasks
            WHERE id = 1
            """
        ).fetchone()[0]

        conn.close()

        assert count == 1
        assert status == "paid"

    finally:
        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            "DELETE FROM payment_transactions WHERE task_id = 1"
        )

        conn.execute(
            "DELETE FROM agent_decisions WHERE task_id = 1"
        )

        conn.execute(
            "UPDATE tasks SET status = 'pending' WHERE id = 1"
        )

        conn.commit()
        conn.close()

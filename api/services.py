import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


def get_dashboard_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute(
            """
            SELECT
                t.id,
                t.name,
                t.amount,
                t.currency,
                t.due_date,
                t.status,
                d.decision,
                d.reason,
                p.status AS payment_status,
                p.reference AS payment_reference
            FROM tasks t

            LEFT JOIN agent_decisions d
                ON d.id = (
                    SELECT MAX(id)
                    FROM agent_decisions
                    WHERE task_id = t.id
                )

            LEFT JOIN payment_transactions p
                ON p.id = (
                    SELECT MAX(id)
                    FROM payment_transactions
                    WHERE task_id = t.id
                )

            ORDER BY t.due_date ASC
            """
        ).fetchall()

        bills = []

        paid_count = 0
        approval_count = 0
        blocked_count = 0

        total_paid = 0
        awaiting_approval = 0
        blocked_amount = 0

        for row in rows:

            bill = {
                "id": row["id"],
                "name": row["name"],
                "amount": row["amount"],
                "currency": row["currency"],
                "due_date": row["due_date"],
                "status": row["status"],
                "decision": row["decision"],
                "reason": row["reason"],
                "payment_status": row["payment_status"],
                "payment_reference": row["payment_reference"],
            }

            bills.append(bill)

            if (
                row["status"] == "paid"
                and row["payment_status"] == "COMPLETED"
            ):
                paid_count += 1
                total_paid += row["amount"]

            elif (
                row["status"] == "pending"
                and row["decision"] == "NEEDS_APPROVAL"
            ):
                approval_count += 1
                awaiting_approval += row["amount"]

            elif (
                row["status"] == "pending"
                and row["decision"] == "BLOCK"
            ):
                blocked_count += 1
                blocked_amount += row["amount"]

        summary = {
            "total_bills": len(bills),
            "paid_count": paid_count,
            "approval_count": approval_count,
            "blocked_count": blocked_count,
            "total_paid": total_paid,
            "awaiting_approval": awaiting_approval,
            "blocked_amount": blocked_amount,
        }

        return {
            "summary": summary,
            "bills": bills,
        }

    finally:
        conn.close()
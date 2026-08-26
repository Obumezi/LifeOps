import sqlite3
from pathlib import Path

from strands import tool


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


@tool
def get_bill_status(task_name: str) -> str:
    """
    Get the current operational status of a specific bill.

    This reads the task, latest agent decision, and latest payment
    transaction directly from the LifeOps database.

    The database is the source of truth.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        task = conn.execute(
            """
            SELECT id, name, amount, currency, due_date, status
            FROM tasks
            WHERE name = ?
            """,
            (task_name,),
        ).fetchone()

        if task is None:
            return f"BILL_NOT_FOUND: No bill named '{task_name}' exists."

        decision = conn.execute(
            """
            SELECT decision, reason
            FROM agent_decisions
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (task["id"],),
        ).fetchone()

        payment = conn.execute(
            """
            SELECT amount, currency, status, reference
            FROM payment_transactions
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (task["id"],),
        ).fetchone()

        result = [
            f"Bill: {task['name']}",
            f"Amount: {task['currency']} {task['amount']:,.0f}",
            f"Due: {task['due_date']}",
            f"Task Status: {task['status']}",
        ]

        if decision:
            result.append(
                f"Decision: {decision['decision']}"
            )
            result.append(
                f"Decision Reason: {decision['reason']}"
            )
        else:
            result.append("Decision: NONE")

        if payment:
            result.append(
                f"Payment Status: {payment['status']}"
            )
            result.append(
                f"Transaction Reference: {payment['reference']}"
            )
        else:
            result.append("Payment Status: NOT_EXECUTED")

        return "\n".join(result)

    finally:
        conn.close()


@tool
def get_paid_bills() -> str:
    """
    Return bills that have actually been paid.

    Payment status is determined from the tasks and
    payment_transactions tables, not from historical bill data.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        rows = conn.execute(
            """
            SELECT
                t.name,
                t.amount,
                t.currency,
                t.due_date,
                p.status,
                p.reference
            FROM tasks t
            INNER JOIN payment_transactions p
                ON p.task_id = t.id
            WHERE p.status = 'COMPLETED'
            ORDER BY t.due_date ASC
            """
        ).fetchall()

        if not rows:
            return "No bills have been paid."

        results = ["=== PAID BILLS ==="]

        for row in rows:
            results.append(
                f"{row['name']} | "
                f"{row['currency']} {row['amount']:,.0f} | "
                f"Status: {row['status']} | "
                f"Reference: {row['reference']}"
            )

        return "\n".join(results)

    finally:
        conn.close()


@tool
def get_pending_approvals() -> str:
    """
    Return bills currently waiting for human approval.

    Only the latest decision for each task is considered.
    """

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
                d.decision,
                d.reason
            FROM tasks t
            INNER JOIN agent_decisions d
                ON d.task_id = t.id
            WHERE d.id IN (
                SELECT MAX(id)
                FROM agent_decisions
                GROUP BY task_id
            )
            AND d.decision = 'NEEDS_APPROVAL'
            AND t.status = 'pending'
            ORDER BY t.due_date ASC
            """
        ).fetchall()

        if not rows:
            return "There are no bills waiting for human approval."

        results = ["=== PENDING APPROVALS ==="]

        for row in rows:
            results.append(
                f"{row['name']} | "
                f"{row['currency']} {row['amount']:,.0f} | "
                f"Due: {row['due_date']} | "
                f"Reason: {row['reason']}"
            )

        return "\n".join(results)

    finally:
        conn.close()

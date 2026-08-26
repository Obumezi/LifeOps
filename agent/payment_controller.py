import sqlite3
from pathlib import Path

from tools.payments import execute_payment


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


def execute_approved_payments() -> list[str]:
    """
    Deterministic payment safety controller.

    Only tasks whose latest decision is explicitly authorized
    are allowed to reach the payment execution tool.

    Authorized decisions:
        - AUTO_HANDLE
        - APPROVED

    Blocked decisions:
        - NEEDS_APPROVAL
        - BLOCK
        - UNKNOWN / any other decision

    Human approval is never performed automatically.
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
                t.status,
                d.decision,
                d.reason
            FROM tasks t
            JOIN agent_decisions d
                ON d.id = (
                    SELECT MAX(d2.id)
                    FROM agent_decisions d2
                    WHERE d2.task_id = t.id
                )
            WHERE t.status = 'pending'
            ORDER BY t.due_date ASC
            """
        ).fetchall()

    finally:
        conn.close()

    results = []

    if not rows:
        results.append(
            "No pending tasks with decisions were found."
        )
        return results

    for row in rows:

        task_id = row["id"]
        task_name = row["name"]
        decision = row["decision"]
        reason = row["reason"]

        if decision == "AUTO_HANDLE":

            result = execute_payment(task_id)
            results.append(result)

        elif decision == "NEEDS_APPROVAL":

            results.append(
                f"APPROVAL_REQUIRED: {task_name} — {reason}"
            )

        elif decision == "BLOCK":

            results.append(
                f"PAYMENT_BLOCKED: {task_name} — {reason}"
            )

        elif decision == "APPROVED":

            result = execute_payment(task_id)
            results.append(result)

        else:

            results.append(
                f"PAYMENT_BLOCKED: {task_name} — "
                f"Unknown decision: {decision}"
            )

    return results


if __name__ == "__main__":

    results = execute_approved_payments()

    print("\n=== LIFEOPS PAYMENT SAFETY CONTROLLER ===\n")

    for result in results:
        print(result)
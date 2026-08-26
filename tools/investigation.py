import json
import sqlite3
from pathlib import Path

from strands import tool

from tools.policy import evaluate_bill_policy
from tools.tasks import get_bill_history


DB_PATH = Path(__file__).resolve().parent.parent / "database" / "lifeops.db"


@tool
def investigate_all_bills() -> str:
    """
    Deterministically investigate every pending financial bill.

    For each pending bill:
    1. Retrieve its payment history.
    2. Evaluate it against the financial safety policy.
    3. Record exactly one agent decision.

    Returns:
        A complete investigation summary for every pending bill.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        tasks = conn.execute(
            """
            SELECT id, name, category, amount, currency, due_date
            FROM tasks
            WHERE status = 'pending'
            ORDER BY due_date ASC
            """
        ).fetchall()
    finally:
        conn.close()

    if not tasks:
        return "No pending financial bills require investigation."

    results = []

    for task in tasks:
        task_id = task["id"]
        task_name = task["name"]
        amount = float(task["amount"])

        # Retrieve historical payments using the existing Strands tool.
        history_text = get_bill_history(task_name)

        # Retrieve numeric history directly from the database.
        conn = sqlite3.connect(DB_PATH)

        try:
            history_rows = conn.execute(
                """
                SELECT amount
                FROM bill_history
                WHERE task_name = ?
                ORDER BY paid_date ASC
                """,
                (task_name,),
            ).fetchall()
        finally:
            conn.close()

        historical_amounts = [
            float(row[0])
            for row in history_rows
        ]

        if not historical_amounts:
            decision = "NEEDS_APPROVAL"
            reason = (
                f"No historical payment data exists for {task_name}. "
                "Human approval is required."
            )

            average_amount = None
            percentage_change = None

        else:
            policy_result = evaluate_bill_policy(
                amount,
                historical_amounts,
            )

            # evaluate_bill_policy returns JSON text.
            if isinstance(policy_result, str):
                policy_result = json.loads(policy_result)

            decision = policy_result["decision"]
            reason = policy_result["reason"]
            average_amount = policy_result["average_amount"]
            percentage_change = policy_result["percentage_change"]

        # Record exactly one decision for this bill.
        conn = sqlite3.connect(DB_PATH)

        try:
            conn.execute(
                """
                INSERT INTO agent_decisions
                (task_id, decision, reason)
                VALUES (?, ?, ?)
                """,
                (
                    task_id,
                    decision,
                    reason,
                ),
            )

            conn.commit()
        finally:
            conn.close()

        results.append(
            {
                "task_id": task_id,
                "bill": task_name,
                "amount": amount,
                "currency": task["currency"],
                "due_date": task["due_date"],
                "decision": decision,
                "reason": reason,
                "average_amount": average_amount,
                "percentage_change": percentage_change,
                "history": history_text,
            }
        )

    lines = [
        "LifeOps completed a deterministic investigation "
        "of every pending financial bill.",
        "",
    ]

    for result in results:
        lines.append(
            f"{result['bill']} | "
            f"{result['currency']} {result['amount']:,.0f} | "
            f"Decision: {result['decision']} | "
            f"Reason: {result['reason']}"
        )

    return "\n".join(lines)
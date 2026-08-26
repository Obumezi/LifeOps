import sqlite3
from pathlib import Path

from strands import tool


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


@tool
def approve_task(task_id: int) -> str:
    """
    Approve a task that previously required human approval.

    The task must have a latest NEEDS_APPROVAL decision.
    Approval changes the latest decision to APPROVED.

    Args:
        task_id: The ID of the task to approve.

    Returns:
        Confirmation of approval or a safety-block message.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:
        task = conn.execute(
            """
            SELECT id, name, amount, currency, status
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        if task is None:
            return (
                f"APPROVAL_BLOCKED: "
                f"Task {task_id} was not found."
            )

        decision = conn.execute(
            """
            SELECT id, decision, reason
            FROM agent_decisions
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (task_id,),
        ).fetchone()

        if decision is None:
            return (
                f"APPROVAL_BLOCKED: "
                f"No agent decision exists for {task['name']}."
            )

        if decision["decision"] != "NEEDS_APPROVAL":
            return (
                f"APPROVAL_BLOCKED: "
                f"{task['name']} does not currently require approval. "
                f"Current decision: {decision['decision']}."
            )

        conn.execute(
            """
            INSERT INTO agent_decisions
            (task_id, decision, reason)
            VALUES (?, ?, ?)
            """,
            (
                task_id,
                "APPROVED",
                "Human approval granted for payment.",
            ),
        )

        conn.commit()

        return (
            f"APPROVED: {task['name']} payment of "
            f"{task['currency']} {task['amount']:,.0f} "
            f"has been approved by the user."
        )

    finally:
        conn.close()
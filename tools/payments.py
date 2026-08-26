import sqlite3
import uuid
from pathlib import Path

from strands import tool


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


@tool
def execute_payment(task_id: int) -> str:
    """
    Execute a simulated payment for a task.

    Payment is allowed only when the latest decision is:
        - AUTO_HANDLE
        - APPROVED

    NEEDS_APPROVAL, BLOCK, and unknown decisions are rejected.

    A task cannot be paid more than once. Idempotency is enforced
    using both the task status and existing COMPLETED transactions.

    The database write is protected by an immediate SQLite transaction
    so concurrent payment attempts cannot both create transactions.

    Args:
        task_id: The ID of the task to pay.

    Returns:
        Payment result or safety-block message.
    """

    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row

    try:
        # ---------------------------------------------------------
        # STEP 0: LOCK DATABASE FOR PAYMENT OPERATION
        # ---------------------------------------------------------

        conn.execute("BEGIN IMMEDIATE")

        # ---------------------------------------------------------
        # STEP 1: GET TASK
        # ---------------------------------------------------------

        task = conn.execute(
            """
            SELECT
                id,
                name,
                amount,
                currency,
                status
            FROM tasks
            WHERE id = ?
            """,
            (task_id,),
        ).fetchone()

        if task is None:
            conn.rollback()

            return (
                f"PAYMENT_BLOCKED: "
                f"Task {task_id} was not found."
            )

        # ---------------------------------------------------------
        # STEP 2: IDEMPOTENCY CHECK
        # ---------------------------------------------------------

        existing_payment = conn.execute(
            """
            SELECT
                id,
                reference
            FROM payment_transactions
            WHERE task_id = ?
              AND status = 'COMPLETED'
            ORDER BY id DESC
            LIMIT 1
            """,
            (task_id,),
        ).fetchone()

        if existing_payment is not None:

            reference = existing_payment["reference"]

            conn.rollback()

            if reference:
                return (
                    f"PAYMENT_BLOCKED: "
                    f"{task['name']} has already been paid. "
                    f"Existing reference: {reference}"
                )

            return (
                f"PAYMENT_BLOCKED: "
                f"{task['name']} already has a completed payment."
            )

        # ---------------------------------------------------------
        # STEP 3: PROTECT AGAINST PAID STATUS
        # ---------------------------------------------------------

        if task["status"] == "paid":

            conn.rollback()

            return (
                f"PAYMENT_BLOCKED: "
                f"{task['name']} is already marked as paid."
            )

        # ---------------------------------------------------------
        # STEP 4: GET LATEST DECISION
        # ---------------------------------------------------------

        decision = conn.execute(
            """
            SELECT
                decision,
                reason
            FROM agent_decisions
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (task_id,),
        ).fetchone()

        if decision is None:

            conn.rollback()

            return (
                f"PAYMENT_BLOCKED: "
                f"No decision exists for {task['name']}."
            )

        current_decision = decision["decision"]

        # ---------------------------------------------------------
        # STEP 5: HARD SAFETY GATE
        # ---------------------------------------------------------

        if current_decision not in {
            "AUTO_HANDLE",
            "APPROVED",
        }:

            conn.rollback()

            return (
                f"PAYMENT_BLOCKED: {task['name']} "
                f"requires human approval. "
                f"Current decision: {current_decision}."
            )

        # ---------------------------------------------------------
        # STEP 6: GENERATE TRANSACTION REFERENCE
        # ---------------------------------------------------------

        reference = (
            f"LIFEOPS-"
            f"{uuid.uuid4().hex[:10].upper()}"
        )

        # ---------------------------------------------------------
        # STEP 7: RECORD PAYMENT
        # ---------------------------------------------------------

        conn.execute(
            """
            INSERT INTO payment_transactions
            (
                task_id,
                amount,
                currency,
                status,
                reference
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                task["id"],
                task["amount"],
                task["currency"],
                "COMPLETED",
                reference,
            ),
        )

        # ---------------------------------------------------------
        # STEP 8: MARK TASK PAID
        # ---------------------------------------------------------

        conn.execute(
            """
            UPDATE tasks
            SET status = 'paid'
            WHERE id = ?
            """,
            (task["id"],),
        )

        # ---------------------------------------------------------
        # STEP 9: COMMIT ATOMIC PAYMENT
        # ---------------------------------------------------------

        conn.commit()

        # ---------------------------------------------------------
        # STEP 10: RESULT
        # ---------------------------------------------------------

        if current_decision == "APPROVED":
            payment_mode = "after human approval"
        else:
            payment_mode = "automatically"

        return (
            f"PAYMENT_COMPLETED: {task['name']} payment of "
            f"{task['currency']} {task['amount']:,.0f} "
            f"was processed {payment_mode}. "
            f"Reference: {reference}"
        )

    except sqlite3.Error as error:

        conn.rollback()

        return (
            f"PAYMENT_BLOCKED: "
            f"Database transaction failed: {error}"
        )

    finally:
        conn.close()
import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


AUTO_PAYMENT_LIMIT = 100000


def get_bill_details(bill_name: str):
    """
    Return a structured explainability view for one LifeOps bill.

    Includes:
    - Current bill state
    - Historical payments
    - Latest agent decision
    - Human approval state
    - Latest payment
    - Historical average
    - Percentage difference from historical average
    - Automatic payment safety limit
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:

        # =========================================================
        # CURRENT BILL
        # =========================================================

        bill = conn.execute(
            """
            SELECT
                id,
                name,
                category,
                amount,
                currency,
                due_date,
                status
            FROM tasks
            WHERE LOWER(name) = LOWER(?)
            """,
            (bill_name,),
        ).fetchone()

        if bill is None:
            return None


        # =========================================================
        # BILL HISTORY
        # =========================================================

        history_rows = conn.execute(
            """
            SELECT
                id,
                amount,
                currency,
                paid_date
            FROM bill_history
            WHERE LOWER(task_name) = LOWER(?)
            ORDER BY paid_date ASC
            """,
            (bill["name"],),
        ).fetchall()


        history = [
            {
                "id": row["id"],
                "amount": row["amount"],
                "currency": row["currency"],
                "paid_date": row["paid_date"],
            }
            for row in history_rows
        ]


        # =========================================================
        # HISTORICAL AVERAGE
        # =========================================================

        historical_average = None
        difference_percentage = None

        if history:

            historical_average = (
                sum(row["amount"] for row in history)
                / len(history)
            )

            if historical_average > 0:

                difference_percentage = (
                    (
                        bill["amount"]
                        - historical_average
                    )
                    / historical_average
                ) * 100


        # =========================================================
        # LATEST DECISION
        # =========================================================

        decision = conn.execute(
            """
            SELECT
                id,
                decision,
                reason,
                created_at
            FROM agent_decisions
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (bill["id"],),
        ).fetchone()


        latest_decision = None

        if decision:

            latest_decision = {
                "id": decision["id"],
                "decision": decision["decision"],
                "reason": decision["reason"],
                "created_at": decision["created_at"],
            }


        # =========================================================
        # ORIGINAL SAFETY DECISION
        #
        # This matters because a bill may currently show APPROVED
        # after human authorization, while the original agent
        # decision was NEEDS_APPROVAL.
        # =========================================================

        original_decision = conn.execute(
            """
            SELECT
                id,
                decision,
                reason,
                created_at
            FROM agent_decisions
            WHERE task_id = ?
            ORDER BY id ASC
            LIMIT 1
            """,
            (bill["id"],),
        ).fetchone()


        original_agent_decision = None

        if original_decision:

            original_agent_decision = {
                "id": original_decision["id"],
                "decision": original_decision["decision"],
                "reason": original_decision["reason"],
                "created_at": original_decision["created_at"],
            }


        # =========================================================
        # HUMAN APPROVAL
        # =========================================================

        approval = conn.execute(
            """
            SELECT
                id,
                decision,
                reason,
                created_at
            FROM agent_decisions
            WHERE task_id = ?
              AND decision = 'APPROVED'
            ORDER BY id DESC
            LIMIT 1
            """,
            (bill["id"],),
        ).fetchone()


        human_approval = None

        if approval:

            human_approval = {
                "approved": True,
                "reason": approval["reason"],
                "created_at": approval["created_at"],
            }

        else:

            human_approval = {
                "approved": False,
                "reason": None,
                "created_at": None,
            }


        # =========================================================
        # LATEST PAYMENT
        # =========================================================

        payment = conn.execute(
            """
            SELECT
                id,
                amount,
                currency,
                status,
                reference,
                created_at
            FROM payment_transactions
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (bill["id"],),
        ).fetchone()


        latest_payment = None

        if payment:

            latest_payment = {
                "id": payment["id"],
                "amount": payment["amount"],
                "currency": payment["currency"],
                "status": payment["status"],
                "reference": payment["reference"],
                "created_at": payment["created_at"],
            }


        # =========================================================
        # RESPONSE
        # =========================================================

        return {

            "bill": {
                "id": bill["id"],
                "name": bill["name"],
                "category": bill["category"],
                "amount": bill["amount"],
                "currency": bill["currency"],
                "due_date": bill["due_date"],
                "status": bill["status"],
            },

            "safety": {
                "automatic_payment_limit":
                    AUTO_PAYMENT_LIMIT,

                "historical_average":
                    round(
                        historical_average,
                        2
                    )
                    if historical_average is not None
                    else None,

                "difference_percentage":
                    round(
                        difference_percentage,
                        2
                    )
                    if difference_percentage is not None
                    else None,

                "exceeds_auto_payment_limit":
                    bill["amount"]
                    > AUTO_PAYMENT_LIMIT,
            },

            "original_decision":
                original_agent_decision,

            "latest_decision":
                latest_decision,

            "human_approval":
                human_approval,

            "payment":
                latest_payment,

            "history":
                history,
        }


    finally:

        conn.close()
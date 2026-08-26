import sqlite3
from pathlib import Path

from strands import tool


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


@tool
def generate_financial_report() -> str:
    """
    Generate a concise operational financial report.

    The database is the source of truth.

    The report shows:
    - Paid bills
    - Bills awaiting approval
    - Blocked bills
    - Total amounts in each category
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
                d.reason,
                p.status AS payment_status
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

        paid = []
        awaiting_approval = []
        blocked = []

        paid_total = 0.0
        approval_total = 0.0
        blocked_total = 0.0

        for row in rows:

            amount = row["amount"]
            currency = row["currency"]

            # -------------------------------------------------
            # PAID
            # -------------------------------------------------

            if (
                row["status"] == "paid"
                and row["payment_status"] == "COMPLETED"
            ):
                paid.append(row)
                paid_total += amount

            # -------------------------------------------------
            # NEEDS APPROVAL
            # -------------------------------------------------

            elif (
                row["status"] == "pending"
                and row["decision"] == "NEEDS_APPROVAL"
            ):
                awaiting_approval.append(row)
                approval_total += amount

            # -------------------------------------------------
            # BLOCKED
            # -------------------------------------------------

            elif (
                row["status"] == "pending"
                and row["decision"] == "BLOCK"
            ):
                blocked.append(row)
                blocked_total += amount

        lines = [
            "=== LIFEOPS FINANCIAL REPORT ===",
            "",
            "PAID",
        ]

        if paid:

            for row in paid:
                lines.append(
                    f"✓ {row['name']} — "
                    f"{row['currency']} "
                    f"{row['amount']:,.0f}"
                )

        else:
            lines.append("None")

        lines.extend(
            [
                "",
                "AWAITING APPROVAL",
            ]
        )

        if awaiting_approval:

            for row in awaiting_approval:
                lines.append(
                    f"! {row['name']} — "
                    f"{row['currency']} "
                    f"{row['amount']:,.0f}"
                )

                if row["reason"]:
                    lines.append(
                        f"  Reason: {row['reason']}"
                    )

        else:
            lines.append("None")

        lines.extend(
            [
                "",
                "BLOCKED",
            ]
        )

        if blocked:

            for row in blocked:
                lines.append(
                    f"✕ {row['name']} — "
                    f"{row['currency']} "
                    f"{row['amount']:,.0f}"
                )

                if row["reason"]:
                    lines.append(
                        f"  Reason: {row['reason']}"
                    )

        else:
            lines.append("None")

        lines.extend(
            [
                "",
                "=== TOTALS ===",
                f"Total paid: NGN {paid_total:,.0f}",
                f"Awaiting approval: NGN {approval_total:,.0f}",
                f"Blocked: NGN {blocked_total:,.0f}",
                "",
                "=== LIFEOPS COMPLETE ===",
            ]
        )

        return "\n".join(lines)

    finally:
        conn.close()
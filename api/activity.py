import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


def get_activity_history(limit: int = 50):
    """
    Return persisted LifeOps activity from:
    - agent_decisions
    - payment_transactions

    Events are returned newest first.
    """

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    try:

        rows = conn.execute(
            """
            SELECT
                d.id AS event_id,
                'decision' AS event_type,
                t.name AS bill_name,
                t.amount AS amount,
                t.currency AS currency,
                d.decision AS status,
                d.reason AS message,
                NULL AS reference,
                d.created_at AS created_at

            FROM agent_decisions d

            JOIN tasks t
                ON t.id = d.task_id


            UNION ALL


            SELECT
                p.id AS event_id,
                'payment' AS event_type,
                t.name AS bill_name,
                p.amount AS amount,
                p.currency AS currency,
                p.status AS status,
                CASE
                    WHEN p.status = 'COMPLETED'
                        THEN 'Payment completed successfully.'
                    ELSE 'Payment transaction recorded.'
                END AS message,
                p.reference AS reference,
                p.created_at AS created_at

            FROM payment_transactions p

            JOIN tasks t
                ON t.id = p.task_id


            ORDER BY created_at DESC, event_id DESC

            LIMIT ?
            """,
            (limit,),
        ).fetchall()


        return [
            {
                "id": row["event_id"],
                "type": row["event_type"],
                "bill_name": row["bill_name"],
                "amount": row["amount"],
                "currency": row["currency"],
                "status": row["status"],
                "message": row["message"],
                "reference": row["reference"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    finally:

        conn.close()
import sqlite3
from pathlib import Path


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


conn = sqlite3.connect(DB_PATH)

try:

    conn.execute("DELETE FROM agent_decisions")
    conn.execute("DELETE FROM payment_transactions")

    conn.execute(
        """
        UPDATE tasks
        SET status = 'pending'
        """
    )

    conn.commit()

    print("LifeOps test environment reset successfully.")

finally:

    conn.close()
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).parent / "lifeops.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)

    # Enforce foreign-key relationships for every connection.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'NGN',
                due_date TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS bill_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                currency TEXT NOT NULL DEFAULT 'NGN',
                paid_date TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_decisions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                decision TEXT NOT NULL,
                reason TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id)
                    REFERENCES tasks(id)
                    ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS payment_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                status TEXT NOT NULL,
                reference TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (task_id)
                    REFERENCES tasks(id)
                    ON DELETE RESTRICT
            )
        """)

        # Indexes used by the LifeOps workflow.
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_tasks_status_due_date
            ON tasks(status, due_date)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_agent_decisions_task_id
            ON agent_decisions(task_id, id DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_payment_transactions_task_id
            ON payment_transactions(task_id, id DESC)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_bill_history_task_name
            ON bill_history(task_name)
        """)

        connection.commit()

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at: {DATABASE_PATH}")
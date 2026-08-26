import sqlite3

from database.db import get_connection, initialize_database


def seed_tasks():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    tasks = [
        (
            "Electricity Bill",
            "utility",
            185000,
            "NGN",
            "2026-08-28",
            "pending",
        ),
        (
            "Internet Subscription",
            "internet",
            25000,
            "NGN",
            "2026-08-29",
            "pending",
        ),
        (
            "Netflix",
            "subscription",
            7000,
            "NGN",
            "2026-08-30",
            "pending",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO tasks
        (name, category, amount, currency, due_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        tasks,
    )

    connection.commit()
    connection.close()

    print(f"Inserted {len(tasks)} tasks into the database.")


if __name__ == "__main__":
    seed_tasks()

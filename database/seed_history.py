from database.db import get_connection, initialize_database


def seed_history():
    initialize_database()

    connection = get_connection()
    cursor = connection.cursor()

    history = [
        # Electricity
        ("Electricity Bill", 121000, "NGN", "2026-05-28"),
        ("Electricity Bill", 128000, "NGN", "2026-06-28"),
        ("Electricity Bill", 134000, "NGN", "2026-07-28"),

        # Internet
        ("Internet Subscription", 24000, "NGN", "2026-05-29"),
        ("Internet Subscription", 25000, "NGN", "2026-06-29"),
        ("Internet Subscription", 25000, "NGN", "2026-07-29"),

        # Netflix
        ("Netflix", 7000, "NGN", "2026-05-30"),
        ("Netflix", 7000, "NGN", "2026-06-30"),
        ("Netflix", 7000, "NGN", "2026-07-30"),
    ]

    cursor.executemany(
        """
        INSERT INTO bill_history
        (task_name, amount, currency, paid_date)
        VALUES (?, ?, ?, ?)
        """,
        history,
    )

    connection.commit()
    connection.close()

    print(f"Inserted {len(history)} historical bills.")


if __name__ == "__main__":
    seed_history()

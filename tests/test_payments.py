import sqlite3

from tools.payments import execute_payment


DB_PATH = "database/lifeops.db"


def test_already_paid_bill_is_idempotent():
    conn = sqlite3.connect(DB_PATH)

    original_task_status = conn.execute(
        "SELECT status FROM tasks WHERE id = 2"
    ).fetchone()[0]

    original_payments = conn.execute(
        """
        SELECT task_id, amount, currency, status, reference, created_at
        FROM payment_transactions
        WHERE task_id = 2
        ORDER BY id
        """
    ).fetchall()

    conn.execute(
        "DELETE FROM payment_transactions WHERE task_id = 2"
    )

    conn.execute(
        "UPDATE tasks SET status = 'paid' WHERE id = 2"
    )

    conn.commit()
    conn.close()

    try:
        result = execute_payment(2)

        assert result.startswith("PAYMENT_BLOCKED")
        assert "already" in result

        conn = sqlite3.connect(DB_PATH)

        after = conn.execute(
            """
            SELECT COUNT(*)
            FROM payment_transactions
            WHERE task_id = 2
            """
        ).fetchone()[0]

        status = conn.execute(
            """
            SELECT status
            FROM tasks
            WHERE id = 2
            """
        ).fetchone()[0]

        conn.close()

        assert after == 0
        assert status == "paid"

    finally:
        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            "DELETE FROM payment_transactions WHERE task_id = 2"
        )

        for payment in original_payments:
            conn.execute(
                """
                INSERT INTO payment_transactions
                (
                    task_id,
                    amount,
                    currency,
                    status,
                    reference,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payment,
            )

        conn.execute(
            "UPDATE tasks SET status = ? WHERE id = 2",
            (original_task_status,),
        )

        conn.commit()
        conn.close()



def test_needs_approval_cannot_execute_payment():
    conn = sqlite3.connect(DB_PATH)

    original_status = conn.execute(
        "SELECT status FROM tasks WHERE id = 1"
    ).fetchone()[0]

    original_payments = conn.execute(
        """
        SELECT task_id, amount, currency, status, reference, created_at
        FROM payment_transactions
        WHERE task_id = 1
        ORDER BY id
        """
    ).fetchall()

    conn.execute(
        "DELETE FROM payment_transactions WHERE task_id = 1"
    )

    conn.execute(
        "UPDATE tasks SET status = 'pending' WHERE id = 1"
    )

    conn.execute(
        "DELETE FROM agent_decisions WHERE task_id = 1"
    )

    conn.execute(
        """
        INSERT INTO agent_decisions
        (task_id, decision, reason)
        VALUES (?, ?, ?)
        """,
        (
            1,
            "NEEDS_APPROVAL",
            "Automated safety test.",
        ),
    )

    conn.commit()
    conn.close()

    try:
        result = execute_payment(1)

        assert result.startswith("PAYMENT_BLOCKED")
        assert "NEEDS_APPROVAL" in result

        conn = sqlite3.connect(DB_PATH)

        payment_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM payment_transactions
            WHERE task_id = 1
            """
        ).fetchone()[0]

        status = conn.execute(
            """
            SELECT status
            FROM tasks
            WHERE id = 1
            """
        ).fetchone()[0]

        conn.close()

        assert payment_count == 0
        assert status == "pending"

    finally:
        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            "DELETE FROM payment_transactions WHERE task_id = 1"
        )

        conn.execute(
            "DELETE FROM agent_decisions WHERE task_id = 1"
        )

        for payment in original_payments:
            conn.execute(
                """
                INSERT INTO payment_transactions
                (
                    task_id,
                    amount,
                    currency,
                    status,
                    reference,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payment,
            )

        conn.execute(
            "UPDATE tasks SET status = ? WHERE id = 1",
            (original_status,),
        )

        conn.commit()
        conn.close()


def test_blocked_bill_cannot_execute_payment():
    conn = sqlite3.connect(DB_PATH)

    original_status = conn.execute(
        "SELECT status FROM tasks WHERE id = 1"
    ).fetchone()[0]

    original_payments = conn.execute(
        """
        SELECT task_id, amount, currency, status, reference, created_at
        FROM payment_transactions
        WHERE task_id = 1
        ORDER BY id
        """
    ).fetchall()

    conn.execute(
        "DELETE FROM payment_transactions WHERE task_id = 1"
    )

    conn.execute(
        "UPDATE tasks SET status = 'pending' WHERE id = 1"
    )

    conn.execute(
        "DELETE FROM agent_decisions WHERE task_id = 1"
    )

    conn.execute(
        """
        INSERT INTO agent_decisions
        (task_id, decision, reason)
        VALUES (?, ?, ?)
        """,
        (
            1,
            "BLOCK",
            "Automated safety test.",
        ),
    )

    conn.commit()
    conn.close()

    try:
        result = execute_payment(1)

        assert result.startswith("PAYMENT_BLOCKED")
        assert "BLOCK" in result

        conn = sqlite3.connect(DB_PATH)

        payment_count = conn.execute(
            """
            SELECT COUNT(*)
            FROM payment_transactions
            WHERE task_id = 1
            """
        ).fetchone()[0]

        status = conn.execute(
            """
            SELECT status
            FROM tasks
            WHERE id = 1
            """
        ).fetchone()[0]

        conn.close()

        assert payment_count == 0
        assert status == "pending"

    finally:
        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            "DELETE FROM payment_transactions WHERE task_id = 1"
        )

        conn.execute(
            "DELETE FROM agent_decisions WHERE task_id = 1"
        )

        for payment in original_payments:
            conn.execute(
                """
                INSERT INTO payment_transactions
                (
                    task_id,
                    amount,
                    currency,
                    status,
                    reference,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payment,
            )

        conn.execute(
            "UPDATE tasks SET status = ? WHERE id = 1",
            (original_status,),
        )

        conn.commit()
        conn.close()


def test_auto_handle_executes_payment_once():
    conn = sqlite3.connect(DB_PATH)

    original_status = conn.execute(
        "SELECT status FROM tasks WHERE id = 2"
    ).fetchone()[0]

    original_payments = conn.execute(
        """
        SELECT task_id, amount, currency, status, reference, created_at
        FROM payment_transactions
        WHERE task_id = 2
        ORDER BY id
        """
    ).fetchall()

    conn.execute(
        "DELETE FROM payment_transactions WHERE task_id = 2"
    )

    conn.execute(
        "UPDATE tasks SET status = 'pending' WHERE id = 2"
    )

    conn.execute(
        "DELETE FROM agent_decisions WHERE task_id = 2"
    )

    conn.execute(
        """
        INSERT INTO agent_decisions
        (task_id, decision, reason)
        VALUES (?, ?, ?)
        """,
        (
            2,
            "AUTO_HANDLE",
            "Automated safety test.",
        ),
    )

    conn.commit()
    conn.close()

    try:
        result = execute_payment(2)

        assert result.startswith("PAYMENT_COMPLETED")
        assert "automatically" in result
        assert "Reference: LIFEOPS-" in result

        conn = sqlite3.connect(DB_PATH)

        payment = conn.execute(
            """
            SELECT amount, currency, status, reference
            FROM payment_transactions
            WHERE task_id = 2
            ORDER BY id DESC
            LIMIT 1
            """
        ).fetchone()

        task_status = conn.execute(
            """
            SELECT status
            FROM tasks
            WHERE id = 2
            """
        ).fetchone()[0]

        conn.close()

        assert payment is not None
        assert payment[0] == 25000
        assert payment[1] == "NGN"
        assert payment[2] == "COMPLETED"
        assert payment[3].startswith("LIFEOPS-")
        assert len(payment[3]) == 18
        assert task_status == "paid"

        second_result = execute_payment(2)

        assert second_result.startswith("PAYMENT_BLOCKED")
        assert "already" in second_result

    finally:
        conn = sqlite3.connect(DB_PATH)

        conn.execute(
            "DELETE FROM payment_transactions WHERE task_id = 2"
        )

        conn.execute(
            "DELETE FROM agent_decisions WHERE task_id = 2"
        )

        for payment in original_payments:
            conn.execute(
                """
                INSERT INTO payment_transactions
                (
                    task_id,
                    amount,
                    currency,
                    status,
                    reference,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                payment,
            )

        conn.execute(
            "UPDATE tasks SET status = ? WHERE id = 2",
            (original_status,),
        )

        conn.commit()
        conn.close()

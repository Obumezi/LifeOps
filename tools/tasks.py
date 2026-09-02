import sqlite3

from strands import tool


DATABASE_PATH = "database/lifeops.db"


@tool
def get_upcoming_tasks() -> str:
    """
    Retrieve the user's upcoming routine tasks from the LifeOps database.

    Returns:
        A formatted list of pending tasks including the authoritative
        database task ID for each obligation.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, name, category, amount, currency, due_date
        FROM tasks
        WHERE status = 'pending'
        ORDER BY due_date ASC
        """
    )

    tasks = cursor.fetchall()

    connection.close()

    if not tasks:
        return "There are no upcoming tasks."

    results = []

    for task_id, name, category, amount, currency, due_date in tasks:
        results.append(
            f"Task ID: {task_id} | "
            f"Name: {name} | "
            f"Category: {category} | "
            f"Amount: {currency} {amount:,} | "
            f"Due: {due_date}"
        )

    return "\n".join(results)

@tool
def get_bill_history(task_name: str) -> str:
    """
    Retrieve historical payment amounts for a specific bill.

    Args:
        task_name: The name of the bill to retrieve history for.

    Returns:
        Historical payment records for the bill.
    """

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT amount, currency, paid_date
        FROM bill_history
        WHERE task_name = ?
        ORDER BY paid_date ASC
        """,
        (task_name,),
    )

    history = cursor.fetchall()

    connection.close()

    if not history:
        return f"No payment history found for {task_name}."

    results = []

    for amount, currency, paid_date in history:
        results.append(
            f"{currency} {amount:,} | Paid: {paid_date}"
        )

    return "\n".join(results)


@tool
def record_decision(
    task_id: int,
    decision: str,
    reason: str,
) -> str:
    """
    Record the latest agent decision for a task.

    Args:
        task_id: The ID of the task.
        decision: One of AUTO_HANDLE, NEEDS_APPROVAL, or BLOCK.
        reason: Explanation for the decision.

    Returns:
        Confirmation that the decision was recorded.
    """

    allowed_decisions = {
        "AUTO_HANDLE",
        "NEEDS_APPROVAL",
        "BLOCK",
    }

    if decision not in allowed_decisions:
        return (
            f"Invalid decision '{decision}'. "
            f"Use one of: {', '.join(sorted(allowed_decisions))}."
        )

    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    # Remove any previous decision for this task.
    cursor.execute(
        """
        DELETE FROM agent_decisions
        WHERE task_id = ?
        """,
        (task_id,),
    )

    # Record the latest decision.
    cursor.execute(
        """
        INSERT INTO agent_decisions
        (task_id, decision, reason)
        VALUES (?, ?, ?)
        """,
        (task_id, decision, reason),
    )

    connection.commit()
    decision_id = cursor.lastrowid

    connection.close()

    return (
        f"Decision recorded successfully. "
        f"Decision ID: {decision_id}"
    )
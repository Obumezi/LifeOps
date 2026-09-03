from strands import tool
from lifeops_tools.state import tasks, BILL_HISTORY


@tool
def get_upcoming_tasks() -> str:
    """
    Retrieve pending LifeOps obligations.

    Returns:
        A formatted list containing the authoritative task ID,
        bill name, category, amount, currency, and due date.
    """

    pending_tasks = [
        task for task in tasks
        if task["status"] == "pending"
    ]

    if not pending_tasks:
        return "There are no upcoming tasks."

    pending_tasks.sort(key=lambda task: task["due_date"])

    results = []

    for task in pending_tasks:
        results.append(
            f"Task ID: {task['id']} | "
            f"Name: {task['name']} | "
            f"Category: {task['category']} | "
            f"Amount: {task['currency']} {task['amount']:,.0f} | "
            f"Due: {task['due_date']}"
        )

    return "\n".join(results)


@tool
def get_bill_history(task_name: str) -> str:
    """
    Retrieve historical amounts for a LifeOps bill.

    Args:
        task_name: Exact bill name.

    Returns:
        Historical bill amounts in chronological order.
    """

    history = BILL_HISTORY.get(task_name)

    if history is None:
        return f"No historical data found for {task_name}."

    formatted = ", ".join(
        f"NGN {amount:,.0f}"
        for amount in history
    )

    return (
        f"Historical amounts for {task_name}: {formatted}"
    )

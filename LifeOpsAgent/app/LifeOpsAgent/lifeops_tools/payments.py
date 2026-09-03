import uuid
from strands import tool
from lifeops_tools import state


@tool
def execute_payment(task_id: int) -> str:
    """
    Execute a LifeOps payment only when a persisted decision
    explicitly authorizes automatic handling.

    Args:
        task_id: Authoritative LifeOps task ID.

    Returns:
        Payment confirmation or PAYMENT_BLOCKED.
    """

    task = state.get_task(task_id)

    if task is None:
        return (
            "PAYMENT_BLOCKED | "
            f"Task ID {task_id} does not exist."
        )

    if task["status"] == "paid":
        return (
            "PAYMENT_BLOCKED | "
            f"Task ID {task_id} is already paid."
        )

    existing_payment = next(
        (
            payment
            for payment in state.payments
            if payment["task_id"] == task_id
            and payment["status"] == "COMPLETED"
        ),
        None,
    )

    if existing_payment is not None:
        return (
            "PAYMENT_BLOCKED | "
            f"A completed payment already exists for Task ID {task_id}."
        )

    latest_decision = next(
        (
            decision
            for decision in reversed(state.decisions)
            if decision["task_id"] == task_id
        ),
        None,
    )

    if latest_decision is None:
        return (
            "PAYMENT_BLOCKED | "
            "No persisted decision exists for this task."
        )

    if latest_decision["decision"] != "AUTO_HANDLE":
        return (
            "PAYMENT_BLOCKED | "
            f"Persisted decision is {latest_decision['decision']}. "
            "Only AUTO_HANDLE may execute automatically."
        )

    payment_reference = f"LIFEOPS-{uuid.uuid4().hex[:10].upper()}"

    payment = {
        "task_id": task_id,
        "task_name": task["name"],
        "amount": task["amount"],
        "currency": task["currency"],
        "status": "COMPLETED",
        "reference": payment_reference,
    }

    state.payments.append(payment)
    task["status"] = "paid"

    return (
        "PAYMENT_COMPLETED | "
        f"Task ID: {task_id} | "
        f"Task: {task['name']} | "
        f"Amount: {task['currency']} {task['amount']:,.0f} | "
        f"Reference: {payment_reference}"
    )

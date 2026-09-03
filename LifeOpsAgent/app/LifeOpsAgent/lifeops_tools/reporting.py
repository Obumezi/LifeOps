from strands import tool
from lifeops_tools import state


@tool
def generate_financial_report() -> str:
    """
    Generate the current LifeOps financial summary.

    Returns:
        Paid total, awaiting approval total, blocked total,
        and per-task status.
    """

    paid_total = sum(
        payment["amount"]
        for payment in state.payments
        if payment["status"] == "COMPLETED"
    )

    awaiting_approval_total = 0.0
    blocked_total = 0.0

    task_lines = []

    for task in state.tasks:
        latest_decision = next(
            (
                decision
                for decision in reversed(state.decisions)
                if decision["task_id"] == task["id"]
            ),
            None,
        )

        decision_name = (
            latest_decision["decision"]
            if latest_decision
            else "NO_DECISION"
        )

        if task["status"] != "paid":
            if decision_name == "NEEDS_APPROVAL":
                awaiting_approval_total += task["amount"]
            elif decision_name == "BLOCK":
                blocked_total += task["amount"]

        task_lines.append(
            f"Task ID: {task['id']} | "
            f"{task['name']} | "
            f"Status: {task['status'].upper()} | "
            f"Decision: {decision_name} | "
            f"Amount: {task['currency']} {task['amount']:,.0f}"
        )

    summary = (
        "LIFEOPS FINANCIAL REPORT\n"
        f"Total Paid: NGN {paid_total:,.0f}\n"
        f"Awaiting Approval: NGN {awaiting_approval_total:,.0f}\n"
        f"Blocked: NGN {blocked_total:,.0f}\n\n"
        + "\n".join(task_lines)
    )

    return summary

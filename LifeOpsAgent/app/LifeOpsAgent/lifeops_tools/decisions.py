from strands import tool
from lifeops_tools import state


ALLOWED_DECISIONS = {
    "AUTO_HANDLE",
    "NEEDS_APPROVAL",
    "BLOCK",
}


@tool
def record_decision(
    task_id: int,
    decision: str,
    reason: str,
) -> str:
    """
    Persist a LifeOps agent decision for a task.

    Args:
        task_id: Authoritative LifeOps task ID.
        decision: AUTO_HANDLE, NEEDS_APPROVAL, or BLOCK.
        reason: Explanation returned by the deterministic policy.

    Returns:
        Confirmation of the persisted decision.
    """

    normalized_decision = decision.strip().upper()

    if normalized_decision not in ALLOWED_DECISIONS:
        return (
            "DECISION_REJECTED | "
            f"Invalid decision: {normalized_decision}"
        )

    task = state.get_task(task_id)

    if task is None:
        return (
            "DECISION_REJECTED | "
            f"Task ID {task_id} does not exist."
        )

    existing = next(
        (
            item
            for item in reversed(state.decisions)
            if item["task_id"] == task_id
        ),
        None,
    )

    if existing is not None:
        return (
            "DECISION_REJECTED | "
            f"A decision already exists for Task ID {task_id}: "
            f"{existing['decision']}."
        )

    decision_id = len(state.decisions) + 1

    record = {
        "id": decision_id,
        "task_id": task_id,
        "task_name": task["name"],
        "decision": normalized_decision,
        "reason": reason,
    }

    state.decisions.append(record)

    return (
        "DECISION_RECORDED | "
        f"Decision ID: {decision_id} | "
        f"Task ID: {task_id} | "
        f"Task: {task['name']} | "
        f"Decision: {normalized_decision} | "
        f"Reason: {reason}"
    )

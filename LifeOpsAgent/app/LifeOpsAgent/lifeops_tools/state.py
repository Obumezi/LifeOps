from copy import deepcopy

INITIAL_TASKS = [
    {
        "id": 1,
        "name": "Electricity Bill",
        "category": "utility",
        "amount": 185000.0,
        "currency": "NGN",
        "due_date": "2026-08-28",
        "status": "pending",
    },
    {
        "id": 2,
        "name": "Internet Subscription",
        "category": "internet",
        "amount": 25000.0,
        "currency": "NGN",
        "due_date": "2026-08-29",
        "status": "pending",
    },
    {
        "id": 3,
        "name": "Netflix",
        "category": "subscription",
        "amount": 7000.0,
        "currency": "NGN",
        "due_date": "2026-08-30",
        "status": "pending",
    },
]

BILL_HISTORY = {
    "Electricity Bill": [121000.0, 128000.0, 134000.0],
    "Internet Subscription": [24000.0, 25000.0, 25000.0],
    "Netflix": [7000.0, 7000.0, 7000.0],
}

tasks = deepcopy(INITIAL_TASKS)
decisions = []
payments = []


def reset_demo_state():
    """Reset the AgentCore demo environment to its original state."""
    global tasks, decisions, payments

    tasks = deepcopy(INITIAL_TASKS)
    decisions = []
    payments = []


def get_task(task_id: int):
    """Return a task by its authoritative ID."""
    return next((task for task in tasks if task["id"] == task_id), None)

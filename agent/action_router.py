import sqlite3
from pathlib import Path

from tools.approval import approve_task
from tools.payments import execute_payment
from tools.status import get_bill_status


DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "lifeops.db"
)


def normalize_bill_name(task_name: str) -> str:
    """
    Normalize common natural-language references to bill names.

    This function only identifies the intended bill.
    It does not approve or execute anything.
    """

    name = task_name.strip()

    # Remove trailing punctuation.
    name = name.rstrip("?!.,").strip()

    lower = name.lower()

    # Remove common conversational prefixes.
    prefixes = [
        "the ",
        "my ",
        "our ",
    ]

    changed = True

    while changed:

        changed = False

        for prefix in prefixes:

            if lower.startswith(prefix):

                name = name[len(prefix):].strip()
                lower = name.lower()
                changed = True
                break

    # Common bill aliases.
    aliases = {
        "electricity": "Electricity Bill",
        "electric bill": "Electricity Bill",
        "electricity bill": "Electricity Bill",
        "power bill": "Electricity Bill",
        "power": "Electricity Bill",
        "electric utility": "Electricity Bill",

        "internet": "Internet Subscription",
        "internet bill": "Internet Subscription",
        "internet subscription": "Internet Subscription",
        "wifi": "Internet Subscription",
        "wi-fi": "Internet Subscription",

        "netflix": "Netflix",
        "netflix subscription": "Netflix",
    }

    if lower in aliases:
        return aliases[lower]

    return name


def resolve_task_id(task_name: str):
    """
    Resolve a natural-language bill name to its task ID.

    Returns:
        int task ID if found, otherwise None.
    """

    normalized_name = normalize_bill_name(task_name)

    conn = sqlite3.connect(DB_PATH)

    try:

        row = conn.execute(
            """
            SELECT id
            FROM tasks
            WHERE LOWER(name) = LOWER(?)
            """,
            (normalized_name,),
        ).fetchone()

        if row is None:
            return None

        return row[0]

    finally:
        conn.close()


def resolve_bill_name(task_name: str):
    """
    Resolve a natural-language bill reference to the
    canonical database bill name.

    Returns:
        canonical bill name if found, otherwise None.
    """

    normalized_name = normalize_bill_name(task_name)

    conn = sqlite3.connect(DB_PATH)

    try:

        row = conn.execute(
            """
            SELECT name
            FROM tasks
            WHERE LOWER(name) = LOWER(?)
            """,
            (normalized_name,),
        ).fetchone()

        if row is None:
            return None

        return row[0]

    finally:
        conn.close()


def approve_bill(task_name: str) -> str:
    """
    Approve a bill by natural-language name.

    The deterministic approval tool remains the authority.
    """

    task_id = resolve_task_id(task_name)

    if task_id is None:

        return (
            f"APPROVAL_FAILED: "
            f"No bill named '{task_name}' was found."
        )

    return approve_task(task_id)


def pay_bill(task_name: str) -> str:
    """
    Attempt to pay a bill by natural-language name.

    The payment controller remains the final safety authority.
    """

    task_id = resolve_task_id(task_name)

    if task_id is None:

        return (
            f"PAYMENT_BLOCKED: "
            f"No bill named '{task_name}' was found."
        )

    return execute_payment(task_id)


def check_bill(task_name: str) -> str:
    """
    Retrieve the current operational status of a bill.

    Bill-name normalization happens before querying the database.
    """

    canonical_name = resolve_bill_name(task_name)

    if canonical_name is None:

        return (
            f"BILL_NOT_FOUND: "
            f"No bill named '{task_name}' exists."
        )

    return get_bill_status(canonical_name)
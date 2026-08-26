from dataclasses import dataclass
import json


from strands import tool


@dataclass
class PolicyResult:
    decision: str
    reason: str
    average_amount: float
    percentage_change: float


AUTO_HANDLE_THRESHOLD = 0.10
MAX_AUTO_PAYMENT = 100000


def evaluate_bill(
    current_amount: float,
    historical_amounts: list[float],
) -> PolicyResult:

    if not historical_amounts:
        return PolicyResult(
            decision="NEEDS_APPROVAL",
            reason="No payment history is available for this bill.",
            average_amount=0,
            percentage_change=0,
        )

    average_amount = sum(historical_amounts) / len(historical_amounts)

    percentage_change = (
        (current_amount - average_amount)
        / average_amount
    )

    if current_amount > MAX_AUTO_PAYMENT:
        return PolicyResult(
            decision="NEEDS_APPROVAL",
            reason=(
                f"Current amount of NGN {current_amount:,.0f} "
                f"exceeds the maximum automatic payment limit "
                f"of NGN {MAX_AUTO_PAYMENT:,.0f}."
            ),
            average_amount=average_amount,
            percentage_change=percentage_change,
        )

    if percentage_change > AUTO_HANDLE_THRESHOLD:
        return PolicyResult(
            decision="NEEDS_APPROVAL",
            reason=(
                f"Current amount of NGN {current_amount:,.0f} "
                f"is {percentage_change:.1%} above the historical "
                f"average of NGN {average_amount:,.0f}."
            ),
            average_amount=average_amount,
            percentage_change=percentage_change,
        )

    return PolicyResult(
        decision="AUTO_HANDLE",
        reason=(
            f"Current amount of NGN {current_amount:,.0f} "
            f"is within the allowed range of the historical "
            f"average of NGN {average_amount:,.0f}."
        ),
        average_amount=average_amount,
        percentage_change=percentage_change,
    )


@tool
def evaluate_bill_policy(
    current_amount: float,
    historical_amounts: list[float],
) -> str:
    """
    Evaluate a bill using LifeOps' deterministic financial safety policy.

    Args:
        current_amount: Current bill amount.
        historical_amounts: Previous payment amounts for the same bill.

    Returns:
        JSON containing the approved decision, average amount,
        percentage change, and reason.
    """

    result = evaluate_bill(
        current_amount=current_amount,
        historical_amounts=historical_amounts,
    )

    return json.dumps({
        "decision": result.decision,
        "reason": result.reason,
        "average_amount": round(result.average_amount, 2),
        "percentage_change": round(
            result.percentage_change * 100,
            2,
        ),
    })
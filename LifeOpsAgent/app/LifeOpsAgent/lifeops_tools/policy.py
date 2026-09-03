from strands import tool


AUTO_PAYMENT_LIMIT = 100000.0
OUTLIER_THRESHOLD_PERCENT = 30.0


@tool
def evaluate_bill_policy(
    current_amount: float,
    historical_amounts: list[float],
) -> str:
    """
    Evaluate a bill using deterministic LifeOps financial policy.

    The policy result is authoritative and must not be overridden
    by the language model.

    Args:
        current_amount: Current bill amount.
        historical_amounts: Previous bill amounts.

    Returns:
        AUTO_HANDLE, NEEDS_APPROVAL, or BLOCK with supporting metrics.
    """

    if current_amount <= 0:
        return (
            "Decision: BLOCK | "
            "Reason: Bill amount must be greater than zero."
        )

    if not historical_amounts:
        return (
            "Decision: NEEDS_APPROVAL | "
            "Reason: No historical billing data is available."
        )

    historical_average = sum(historical_amounts) / len(historical_amounts)

    difference_percent = (
        ((current_amount - historical_average) / historical_average) * 100
        if historical_average > 0
        else 0
    )

    if current_amount > AUTO_PAYMENT_LIMIT:
        decision = "NEEDS_APPROVAL"
        reason = (
            f"Current amount exceeds the automatic payment limit "
            f"of NGN {AUTO_PAYMENT_LIMIT:,.0f}."
        )
    elif difference_percent > OUTLIER_THRESHOLD_PERCENT:
        decision = "NEEDS_APPROVAL"
        reason = (
            f"Current amount is {difference_percent:.2f}% above the "
            f"historical average, exceeding the "
            f"{OUTLIER_THRESHOLD_PERCENT:.0f}% threshold."
        )
    else:
        decision = "AUTO_HANDLE"
        reason = "Bill is within automatic payment policy."

    return (
        f"Decision: {decision} | "
        f"Current Amount: NGN {current_amount:,.2f} | "
        f"Historical Average: NGN {historical_average:,.2f} | "
        f"Difference: {difference_percent:.2f}% | "
        f"Auto Payment Limit: NGN {AUTO_PAYMENT_LIMIT:,.2f} | "
        f"Reason: {reason}"
    )

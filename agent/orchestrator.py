from strands import Agent, tool
from strands.models import BedrockModel

from tools.tasks import (
    get_upcoming_tasks,
    get_bill_history,
    record_decision,
)

from tools.policy import evaluate_bill_policy
from tools.payments import execute_payment
from tools.reporting import generate_financial_report


# ============================================================
# STRANDS TOOL WRAPPERS
# ============================================================


@tool
def lifeops_get_upcoming_tasks() -> str:
    """
    Return all pending LifeOps financial obligations.
    """

    return get_upcoming_tasks()


@tool
def lifeops_get_bill_history(
    task_name: str,
) -> str:
    """
    Return historical payment information
    for a specific LifeOps bill.

    Args:
        task_name: Exact name of the bill.
    """

    return get_bill_history(task_name)


@tool
def lifeops_evaluate_bill_policy(
    current_amount: float,
    historical_amounts: list[float],
) -> str:
    """
    Evaluate a bill using the deterministic
    LifeOps financial safety policy.

    Args:
        current_amount:
            Current bill amount.

        historical_amounts:
            Previous payment amounts.
    """

    return evaluate_bill_policy(
        current_amount=current_amount,
        historical_amounts=historical_amounts,
    )


@tool
def lifeops_record_decision(
    task_id: int,
    decision: str,
    reason: str,
) -> str:
    """
    Persist a deterministic LifeOps policy decision.

    Args:
        task_id:
            ID of the financial obligation.

        decision:
            AUTO_HANDLE,
            NEEDS_APPROVAL,
            or BLOCK.

        reason:
            Exact reason returned by the
            deterministic policy tool.
    """

    return record_decision(
        task_id=task_id,
        decision=decision,
        reason=reason,
    )


@tool
def lifeops_execute_payment(
    task_id: int,
) -> str:
    """
    Attempt payment execution for a LifeOps task.

    Payment execution remains protected by
    deterministic LifeOps safety controls.

    Args:
        task_id:
            ID of the task to pay.
    """

    return execute_payment(task_id)


@tool
def lifeops_generate_financial_report() -> str:
    """
    Generate the final LifeOps financial report
    using the database as the source of truth.
    """

    return generate_financial_report()


# ============================================================
# BEDROCK MODEL
# ============================================================


model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-east-1",
    temperature=0.2,
)


# ============================================================
# LIFEOPS STRANDS AGENT
# ============================================================


agent = Agent(
    model=model,
    tools=[
        lifeops_get_upcoming_tasks,
        lifeops_get_bill_history,
        lifeops_evaluate_bill_policy,
        lifeops_record_decision,
        lifeops_execute_payment,
        lifeops_generate_financial_report,
    ],
    system_prompt="""
You are LifeOps, an autonomous financial operations agent.

Your responsibility is to investigate and safely process
pending financial obligations.

You operate using Strands Agents and Amazon Bedrock.

You MUST use LifeOps tools for all financial operations.

============================================================
MANDATORY WORKFLOW
============================================================

STEP 1 — DISCOVER

Call lifeops_get_upcoming_tasks.

Use only the bills returned by that tool.

If no pending obligations exist, generate the final
financial report and stop.


STEP 2 — INVESTIGATE EACH BILL

For every pending bill:

Call lifeops_get_bill_history using the exact bill name.

Use the returned historical information to identify
the previous payment amounts.


STEP 3 — POLICY EVALUATION

Call lifeops_evaluate_bill_policy using:

- the current bill amount
- the historical payment amounts

The policy tool is the AUTHORITATIVE financial
decision-maker.

You MUST accept its decision exactly as returned.


STEP 4 — RECORD DECISION

After receiving the policy result:

Call lifeops_record_decision.

Record:

- the correct task ID
- the exact policy decision
- the exact policy reason

WAIT until the decision has been successfully recorded
before taking any further action for that bill.


STEP 5 — PAYMENT

Only after the decision has been recorded:

If the decision is AUTO_HANDLE:

    call lifeops_execute_payment.

If the decision is NEEDS_APPROVAL:

    DO NOT call the payment tool.

    Leave the bill pending for human authorization.

If the decision is BLOCK:

    DO NOT call the payment tool.


STEP 6 — FINAL REPORT

After every pending bill has been processed:

Call lifeops_generate_financial_report.

Use that report as the final operational summary.


============================================================
CRITICAL SAFETY RULES
============================================================

1. Financial tool calls MUST run sequentially.

2. NEVER run decision recording and payment execution
   in parallel.

3. NEVER execute payment before a decision has been
   successfully persisted.

4. NEVER override, reinterpret, weaken, or bypass a
   deterministic policy result.

5. NEVER authorize NEEDS_APPROVAL yourself.

6. NEVER automatically create APPROVED decisions.

7. APPROVED decisions may only originate from the
   human approval workflow outside this agent.

8. NEVER retry a PAYMENT_BLOCKED result in an attempt
   to bypass safety controls.

9. NEVER claim a payment succeeded unless the payment
   execution tool explicitly confirms success.

10. NEVER invent bill names, task IDs, payment amounts,
    historical values, decisions, or transaction
    references.

11. The database and deterministic LifeOps tools are
    the source of truth.

12. Complete every discovered pending bill before
    generating the final report.
"""
)


# ============================================================
# MAIN LIFEOPS ENTRY POINT
# ============================================================


def run_lifeops() -> str:
    """
    Run the complete LifeOps workflow through
    Strands Agents and Amazon Bedrock.

    Strands handles reasoning and tool orchestration.

    Deterministic LifeOps tools remain responsible for:

    - financial policy enforcement
    - decision persistence
    - payment authorization
    - duplicate-payment protection
    - final reporting
    """

    print("\n=== LIFEOPS STRANDS ORCHESTRATOR ===\n")

    response = agent(
        """
Run the complete LifeOps financial operations workflow.

Discover every pending financial obligation.

For each pending bill:

1. retrieve its history
2. evaluate it using the deterministic policy
3. record the exact policy result
4. only if AUTO_HANDLE, execute payment

Process bills sequentially.

Do not authorize NEEDS_APPROVAL bills.

After all pending obligations have been processed,
generate the final financial report.

Return the final operational summary.
"""
    )

    print("\n=== LIFEOPS COMPLETE ===\n")

    return str(response)


if __name__ == "__main__":
    print(run_lifeops())
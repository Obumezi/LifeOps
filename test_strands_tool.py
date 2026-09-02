from strands import Agent, tool
from strands.models import BedrockModel

from tools.policy import evaluate_bill_policy
from tools.tasks import record_decision
from tools.payments import execute_payment


@tool
def lifeops_evaluate_bill_policy(
    current_amount: float,
    historical_amounts: list[float],
) -> str:
    """
    Evaluate a bill using LifeOps' deterministic
    financial safety policy.

    Args:
        current_amount: Current bill amount.
        historical_amounts: Previous bill amounts.
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
    Persist an authoritative LifeOps policy decision.

    Args:
        task_id: ID of the bill.
        decision: AUTO_HANDLE, NEEDS_APPROVAL, or BLOCK.
        reason: Exact policy reason.
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
    Attempt to execute payment for a LifeOps bill.

    Payment safety rules are enforced inside
    the deterministic payment tool.

    Args:
        task_id: ID of the bill to pay.
    """

    return execute_payment(task_id)


model = BedrockModel(
    model_id="global.anthropic.claude-sonnet-4-6",
    region_name="us-east-1",
    temperature=0.2,
)


agent = Agent(
    model=model,
    tools=[
        lifeops_evaluate_bill_policy,
        lifeops_record_decision,
        lifeops_execute_payment,
    ],
    system_prompt="""
You are LifeOps, an autonomous financial operations agent.

You must follow the LifeOps financial workflow STRICTLY
and SEQUENTIALLY.

MANDATORY EXECUTION ORDER:

STEP 1:
Call lifeops_evaluate_bill_policy.

WAIT for the tool result before doing anything else.

STEP 2:
Read the exact policy decision and reason returned
by the policy tool.

Call lifeops_record_decision.

WAIT for lifeops_record_decision to finish successfully.

DO NOT call any other tool at the same time as
lifeops_record_decision.

STEP 3:
Only after the decision-recording tool has successfully
completed:

- If the recorded decision is AUTO_HANDLE,
  call lifeops_execute_payment.

- If the recorded decision is NEEDS_APPROVAL,
  do not call the payment tool.

- If the recorded decision is BLOCK,
  do not call the payment tool.

CRITICAL SAFETY RULES:

1. Tool calls in this workflow MUST NOT run in parallel.

2. Never call lifeops_record_decision and
   lifeops_execute_payment simultaneously.

3. A payment must never be attempted until the
   authoritative decision has been persisted.

4. Never override the deterministic policy result.

5. Never retry or bypass a blocked payment.

6. Never claim that payment succeeded unless
   lifeops_execute_payment explicitly confirms success.

7. The deterministic LifeOps tools are authoritative.
"""
)


response = agent(
    """
Process this LifeOps obligation end-to-end:

Task ID: 2
Bill: Internet Subscription
Current amount: 25000 NGN

Historical payments:
24000
25000
25000

Execute the workflow STRICTLY IN SEQUENCE.

First:
evaluate the bill and wait for the result.

Second:
record the exact policy decision and wait until
the recording tool confirms it has finished.

Third:
only if the recorded decision is AUTO_HANDLE,
execute the payment.

DO NOT execute the decision-recording tool and
payment tool in parallel.

Report the final outcome.
"""
)


print("\n=== LIFEOPS STRANDS AUTO PAYMENT TEST ===\n")
print(response)
print("\n=========================================\n")
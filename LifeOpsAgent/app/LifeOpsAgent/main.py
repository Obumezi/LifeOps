from typing import Any
from collections import OrderedDict

from strands import Agent
from strands.agent.conversation_manager.null_conversation_manager import (
    NullConversationManager,
)
from bedrock_agentcore.runtime import BedrockAgentCoreApp

from model.load import load_model

from lifeops_tools.tasks import (
    get_upcoming_tasks,
    get_bill_history,
)
from lifeops_tools.policy import evaluate_bill_policy
from lifeops_tools.decisions import record_decision
from lifeops_tools.payments import execute_payment
from lifeops_tools.reporting import generate_financial_report
from lifeops_tools.state import reset_demo_state


app = BedrockAgentCoreApp()
log = app.logger


DEFAULT_SYSTEM_PROMPT = """
You are LifeOps, an autonomous financial operations agent.

Your responsibility is to review pending household obligations,
evaluate them using deterministic financial policy, safely handle
routine payments, escalate risky obligations, and produce a final
financial report.

STRICT SAFETY RULES:

1. Always call get_upcoming_tasks before processing obligations.

2. Use the Task ID returned by get_upcoming_tasks.
   Never guess, infer, invent, or substitute a task ID.

3. For every pending bill:
   - retrieve its history using get_bill_history
   - evaluate it using evaluate_bill_policy

4. evaluate_bill_policy is authoritative.
   Never override, reinterpret, weaken, or ignore its decision.

5. After policy evaluation, persist the exact decision using
   record_decision.

6. Financial mutations must be sequential.

   For each task:
       evaluate policy
       then record decision
       wait for record_decision to complete
       then, only when decision is AUTO_HANDLE,
       call execute_payment

7. Never call record_decision and execute_payment in parallel.

8. Never execute payment before a decision has been persisted.

9. If the decision is NEEDS_APPROVAL:
   - do not execute payment
   - leave the obligation pending for human review

10. If the decision is BLOCK:
    - do not execute payment

11. Only AUTO_HANDLE may result in automatic payment.

12. Never create or fabricate an APPROVED decision.
    Human approval exists outside this AgentCore workflow.

13. If execute_payment returns PAYMENT_BLOCKED:
    do not retry in an attempt to bypass the safety control.

14. Never claim a payment succeeded unless execute_payment
    explicitly returns PAYMENT_COMPLETED.

15. Never invent bills, payment references, history values,
    decisions, or execution results.

16. The tools and application state are the source of truth.

17. Process every pending obligation before generating the report.

18. After all obligations are processed, call
    generate_financial_report and use that result as the basis
    of your final response.

Your final response should be concise and clearly identify:
- what was automatically handled
- what requires human approval
- total amount paid
- amount awaiting approval
"""


tools = [
    get_upcoming_tasks,
    get_bill_history,
    evaluate_bill_policy,
    record_decision,
    execute_payment,
    generate_financial_report,
]


def _make_conversation_manager():
    return NullConversationManager()


def agent_factory():
    cache = OrderedDict()

    def get_or_create_agent(session_id):
        if session_id in cache:
            cache.move_to_end(session_id)
            return cache[session_id]

        if len(cache) >= 128:
            cache.popitem(last=False)

        cache[session_id] = Agent(
            model=load_model(),
            system_prompt=DEFAULT_SYSTEM_PROMPT,
            tools=tools,
            conversation_manager=_make_conversation_manager(),
        )

        return cache[session_id]

    return get_or_create_agent


get_or_create_agent = agent_factory()


def strip_trailing_tool_use(messages: Any) -> list[dict]:
    """Strip toolUse blocks from the tail until the last message has none."""

    if not isinstance(messages, list):
        raise ValueError("messages must be a list")

    messages = list(messages)

    while messages:
        last = messages[-1]

        if not isinstance(last, dict):
            raise ValueError("each message must be an object")

        original_content = last.get("content", [])

        if not isinstance(original_content, list) or not all(
            isinstance(block, dict)
            for block in original_content
        ):
            raise ValueError(
                "each message content value must be a list of content blocks"
            )

        content = [
            block
            for block in original_content
            if "toolUse" not in block
        ]

        if len(content) == len(original_content):
            break

        if content:
            messages[-1] = {
                **last,
                "content": content,
            }
            break

        messages.pop()

    return messages


def _extract_prompt(payload: dict):
    """Accept harness messages, tool results, or a plain prompt string."""

    if not isinstance(payload, dict):
        raise ValueError("payload must be a JSON object")

    if "messages" in payload:
        return strip_trailing_tool_use(payload["messages"])

    if "tool_results" in payload:
        tool_results = payload["tool_results"]

        if not isinstance(tool_results, list) or not all(
            isinstance(tool_result, dict)
            and isinstance(tool_result.get("toolUseId"), str)
            for tool_result in tool_results
        ):
            raise ValueError(
                "tool_results must contain objects with a toolUseId string"
            )

        return [
            {
                "role": "user",
                "content": [
                    {
                        "toolResult": {
                            "toolUseId": tr["toolUseId"],
                            "status": tr.get("status", "success"),
                            "content": tr.get("content", []),
                        }
                    }
                    for tr in tool_results
                ],
            }
        ]

    prompt = payload.get("prompt", "")

    if not isinstance(prompt, str):
        raise ValueError("prompt must be a string")

    return prompt


@app.entrypoint
async def invoke(payload, context):
    log.info("Invoking LifeOps AgentCore agent")

    session_id = getattr(
        context,
        "session_id",
        "default-session",
    )

    agent = get_or_create_agent(session_id)

    prompt = _extract_prompt(payload)

    if isinstance(prompt, str) and prompt.strip().lower() in {
        "run lifeops",
        "run",
        "execute",
        "process bills",
    }:
        reset_demo_state()

        prompt = """
Run the complete LifeOps workflow now.

Process every pending obligation.

For each obligation:
1. retrieve history
2. evaluate deterministic policy
3. persist the policy decision
4. if and only if the decision is AUTO_HANDLE,
   execute payment
5. if NEEDS_APPROVAL or BLOCK, do not pay

Critical financial mutations must happen sequentially.

After every bill has been processed, generate the financial report
and summarize the outcome.
"""

    async for event in agent.stream_async(prompt):
        if not isinstance(event, dict) or "event" not in event:
            continue

        cbs = event["event"].get("contentBlockStart")

        if cbs is not None and not cbs.get("start"):
            continue

        yield event


if __name__ == "__main__":
    app.run()
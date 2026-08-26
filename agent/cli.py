from strands import Agent

from tools.tasks import (
    get_upcoming_tasks,
    get_bill_history,
    record_decision,
)

from tools.policy import evaluate_bill_policy

from tools.status import (
    get_bill_status,
    get_paid_bills,
    get_pending_approvals,
)

from tools.reporting import generate_financial_report

from agent.action_router import (
    approve_bill,
    pay_bill,
    check_bill,
)

from agent.orchestrator import run_lifeops


def create_agent():
    """
    Create the LifeOps natural-language information agent.

    The AI can investigate and explain financial information.

    It does NOT have direct access to approval or payment tools.
    """

    return Agent(
        model="us.amazon.nova-2-lite-v1:0",
        tools=[
            get_upcoming_tasks,
            get_bill_history,
            evaluate_bill_policy,
            record_decision,
            get_bill_status,
            get_paid_bills,
            get_pending_approvals,
        ],
    )


def handle_natural_language(agent, request):
    """
    Handle informational questions using the LifeOps AI agent.

    Financial actions are handled separately by the deterministic
    action router.
    """

    response = agent(
        f"""
        You are LifeOps, a personal operations assistant.

        The user said:

        "{request}"

        Follow these rules exactly:

        1. The LifeOps database is the source of truth.

        2. Never invent financial information.

        3. Never invent operational policies.

        4. Historical payment data describes past payments only.

        5. If the user asks about the current status of a specific
           bill, call get_bill_status().

        6. If the user asks which bills have been paid,
           call get_paid_bills().

        7. If the user asks which bills are waiting for approval,
           call get_pending_approvals().

        8. If the user asks why a bill has not been paid,
           call get_bill_status().

        9. Never claim a payment is completed unless the database
           explicitly reports COMPLETED.

        10. Never approve a payment.

        11. Never execute a payment.

        12. Never reinterpret a policy decision.

        13. Never describe historical payments as current payments.

        14. Never say a bill was paid merely because it appears
            in historical bill history.

        15. Answer concisely and use actual LifeOps tool results.

        Financial actions such as approval and payment are handled
        outside the AI by the deterministic LifeOps action router.
        """
    )

    return str(response)


def detect_action(request):
    """
    Detect a user's requested financial action.

    This function does NOT execute anything.

    Returns:

        ("approve", bill_name)
        ("pay", bill_name)
        ("check", bill_name)

    or:

        (None, None)
    """

    text = request.strip()

    if not text:
        return None, None

    # Remove trailing punctuation.
    cleaned = text.rstrip("?!.,").strip()
    lower = cleaned.lower()

    # ---------------------------------------------------------
    # APPROVAL INTENT
    # ---------------------------------------------------------

    approval_phrases = [
        "i want to approve the ",
        "i want to approve ",
        "please approve the ",
        "please approve ",
        "approve payment for the ",
        "approve payment for ",
        "approve the payment for the ",
        "approve the payment for ",
        "approve the bill ",
        "approve bill ",
        "approve my bill ",
        "approve my ",
        "approve the ",
        "approve ",
        "i approve the ",
        "i approve ",
    ]

    for phrase in approval_phrases:

        if lower.startswith(phrase):

            bill_name = cleaned[len(phrase):].strip()

            if bill_name:
                return "approve", bill_name

    # ---------------------------------------------------------
    # PAYMENT INTENT
    # ---------------------------------------------------------

    payment_phrases = [
        "can you pay the ",
        "can you pay my ",
        "can you pay ",
        "please pay the ",
        "please pay my ",
        "please pay ",
        "i want to pay the ",
        "i want to pay my ",
        "i want to pay ",
        "make a payment for the ",
        "make a payment for ",
        "make payment for the ",
        "make payment for ",
        "pay the bill ",
        "pay bill ",
        "pay my bill ",
        "pay the ",
        "pay my ",
        "pay ",
    ]

    for phrase in payment_phrases:

        if lower.startswith(phrase):

            bill_name = cleaned[len(phrase):].strip()

            if bill_name:
                return "pay", bill_name

    # ---------------------------------------------------------
    # CHECK / STATUS INTENT
    # ---------------------------------------------------------

    # First handle questions that contain "been paid",
    # "paid", "processed", or "settled".

    paid_questions = [
        "has the ",
        "has my ",
        "has ",
        "is the ",
        "is my ",
        "is ",
    ]

    payment_status_suffixes = [
        " been paid",
        " paid",
        " been processed",
        " processed",
        " been settled",
        " settled",
    ]

    for phrase in paid_questions:

        if lower.startswith(phrase):

            bill_name = cleaned[len(phrase):].strip()

            for suffix in payment_status_suffixes:

                if bill_name.lower().endswith(suffix):

                    bill_name = bill_name[
                        : -len(suffix)
                    ].strip()

                    if bill_name:
                        return "check", bill_name

    # ---------------------------------------------------------
    # STANDARD STATUS QUESTIONS
    # ---------------------------------------------------------

    status_phrases = [
        "what is the status of the ",
        "what is the status of ",
        "what's the status of the ",
        "what's the status of ",
        "whats the status of the ",
        "whats the status of ",
        "show me the status of the ",
        "show me the status of ",
        "show the status of the ",
        "show the status of ",
        "check the status of the ",
        "check the status of ",
        "check status of the ",
        "check status of ",
        "status of the ",
        "status of ",
        "check the ",
        "check ",
    ]

    for phrase in status_phrases:

        if lower.startswith(phrase):

            bill_name = cleaned[len(phrase):].strip()

            if bill_name:
                return "check", bill_name

    return None, None


def execute_action(action, bill_name):
    """
    Execute an action through the deterministic safety router.

    The AI never performs the financial operation directly.
    """

    if action == "approve":

        return approve_bill(bill_name)

    if action == "pay":

        return pay_bill(bill_name)

    if action == "check":

        return check_bill(bill_name)

    return "ACTION_NOT_RECOGNIZED"


def detect_workflow_request(request):
    """
    Detect requests asking LifeOps to investigate bills
    and safely handle automatically authorized payments.

    Returns True when the request should use the deterministic
    safe payment workflow.
    """

    text = request.strip().lower()

    workflow_phrases = [
        "handle my bills",
        "handle my bill",
        "handle bills",
        "run my bills",
        "run the bills",
        "run my financial operations",
        "run lifeops",
        "process my bills",
        "process the bills",
        "process my financial obligations",
        "check everything and handle what you safely can",
        "check my bills and pay what you can",
        "pay whatever can be safely handled",
        "handle whatever can be safely handled",
        "take care of my bills",
        "take care of the bills",
    ]

    for phrase in workflow_phrases:

        if phrase in text:
            return True

    return False



def show_help():

    print(
        """
=== LIFEOPS COMMANDS ===

You can use natural language, for example:

  What bills are coming up?
  Which bills can you pay automatically?
  Why hasn't the electricity bill been paid?
  Which bills have already been paid?
  Which bills are waiting for my approval?
  What is the status of the electricity bill?
  Has the electricity bill been paid?
  Can you pay the electricity bill?
  I want to approve the electricity bill.

System commands:

  status
      Show the current financial report.

  bills
      Show the current financial report.

  run
      Run the complete LifeOps workflow.

  approve <bill name>
      Approve a bill requiring human approval.

  pay <bill name>
      Execute an authorized payment.

  report
      Generate the financial report.

  help
      Show this help message.

  exit
      Exit LifeOps.
"""
    )


def main():

    print("\n=== LIFEOPS INTERACTIVE MODE ===")
    print("Ask LifeOps anything about your financial operations.")
    print("Type 'help' for commands or 'exit' to quit.\n")

    agent = create_agent()

    while True:

        try:

            request = input("LifeOps> ").strip()

        except (KeyboardInterrupt, EOFError):

            print("\nExiting LifeOps.")
            break

        if not request:
            continue

        parts = request.split()
        command = parts[0].lower()

        # ---------------------------------------------------------
        # EXIT
        # ---------------------------------------------------------

        if command == "exit":

            print("Exiting LifeOps.")
            break

        # ---------------------------------------------------------
        # HELP
        # ---------------------------------------------------------

        if command == "help":

            show_help()
            continue

        # ---------------------------------------------------------
        # REPORT
        # ---------------------------------------------------------

        if command in {"status", "report", "bills"}:

            print()
            print(generate_financial_report())
            continue

        # ---------------------------------------------------------
        # RUN
        # ---------------------------------------------------------

        if command == "run":


            print()
            run_lifeops()
            continue

        # ---------------------------------------------------------
        # NATURAL-LANGUAGE WORKFLOW
        # ---------------------------------------------------------

        if detect_workflow_request(request):

            print()

            try: 

                run_lifeops()

            except Exception as error:

                print(
                    "LifeOps encountered an error while processing "
                    f"your request: {error}"
                )

            continue


        # ---------------------------------------------------------
        # NATURAL-LANGUAGE ACTION
        # ---------------------------------------------------------

        action, bill_name = detect_action(request)

        if action:

            print()
            print(
                execute_action(
                    action,
                    bill_name,
                )
            )

            continue

        # ---------------------------------------------------------
        # NATURAL-LANGUAGE QUESTION
        # ---------------------------------------------------------

        print()

        try:

            response = handle_natural_language(
                agent,
                request,
            )

            print(response)

        except Exception as error:

            print(
                "LifeOps encountered an error while processing "
                f"your request: {error}"
            )


if __name__ == "__main__":
    main()
from tools.investigation import investigate_all_bills
from tools.reporting import generate_financial_report
from agent.payment_controller import execute_approved_payments


def run_lifeops() -> str:
    """
    Run the complete LifeOps financial operations workflow.

    Workflow:

        1. Investigate pending bills.
        2. Pass current decisions to the deterministic
           payment safety controller.
        3. Generate the final financial report.

    The orchestrator does not approve or execute payments
    directly. Payment authorization is enforced by the
    payment safety controller.
    """

    results = []

    print("\n=== LIFEOPS ORCHESTRATOR ===\n")

    # ============================================================
    # STEP 1: INVESTIGATION
    # ============================================================

    print("=== STEP 1: INVESTIGATION ===")

    investigation_result = investigate_all_bills()

    print(investigation_result)

    results.append(investigation_result)

    # ============================================================
    # STEP 2: PAYMENT SAFETY CONTROLLER
    # ============================================================

    print("\n=== STEP 2: PAYMENT SAFETY CONTROLLER ===")

    payment_results = execute_approved_payments()

    for result in payment_results:
        print(result)

    results.extend(payment_results)

    # ============================================================
    # STEP 3: FINANCIAL REPORT
    # ============================================================

    print("\n=== STEP 3: FINANCIAL REPORT ===")

    financial_report = generate_financial_report()

    print(financial_report)

    results.append(financial_report)

    print("\n=== LIFEOPS COMPLETE ===")

    return "\n".join(results)


if __name__ == "__main__":
    run_lifeops()
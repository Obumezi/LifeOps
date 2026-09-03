# LifeOps

> **An autonomous AI agent for managing routine financial obligations safely, escalating only when human judgment is required.**

LifeOps is an AI-powered financial operations agent built with **Strands Agents, Amazon Bedrock, Amazon Bedrock AgentCore, FastAPI, and SQLite**.

Instead of simply reminding a user that a bill is due, LifeOps investigates the obligation, reviews historical spending, evaluates deterministic safety policies, decides whether the obligation can be handled automatically, executes approved payments, and escalates unusual or high-value transactions for human approval.

The project demonstrates **bounded AI autonomy**: the AI agent can reason and orchestrate workflows, but it cannot override deterministic financial controls.

---

# 1. The Problem

Many recurring financial tasks are predictable:

- electricity bills
- internet subscriptions
- streaming subscriptions
- recurring service payments
- routine household expenses

Traditional reminder applications still require the user to manually:

1. review the bill,
2. determine whether the amount looks normal,
3. decide whether it should be paid,
4. execute the payment,
5. keep track of what has already been handled.

An autonomous agent could perform much of this work.

However, allowing an LLM unrestricted access to financial execution introduces significant risk.

LifeOps addresses both problems.

It automates routine obligations while keeping deterministic safety controls between AI reasoning and financial execution.

---

# 2. Core Idea

LifeOps follows a simple principle:

> **AI decides what should happen. Deterministic controls decide what is allowed to happen.**

The Strands agent orchestrates the workflow.

It can:

- discover pending obligations,
- retrieve historical bill information,
- request policy evaluation,
- persist decisions,
- initiate permitted payments,
- generate financial reports.

However, the LLM does **not** have unrestricted authority to execute payments.

Financial actions are protected by deterministic tools and policies.

For example:

```text
Current bill
     │
     ▼
Historical analysis
     │
     ▼
Deterministic policy evaluation
     │
     ├── AUTO_HANDLE ───────► Payment allowed
     │
     ├── NEEDS_APPROVAL ────► Human approval required
     │
     └── BLOCK ─────────────► Payment prohibited
```

This creates a bounded-autonomy architecture where AI provides intelligence and orchestration without becoming the final authority over sensitive financial actions.

---

# 3. Demo Scenario

LifeOps currently demonstrates the workflow using three financial obligations.

| Bill | Amount | Expected Behaviour |
|---|---:|---|
| Electricity Bill | ₦185,000 | Requires human approval |
| Internet Subscription | ₦25,000 | Automatically handled |
| Netflix | ₦7,000 | Automatically handled |

Historical Electricity payments:

```text
₦121,000
₦128,000
₦134,000
```

Historical average:

```text
≈ ₦127,666.67
```

Current Electricity bill:

```text
₦185,000
```

Increase above historical average:

```text
≈ 44.91%
```

LifeOps therefore refuses to automatically pay the Electricity bill.

The deterministic policy returns:

```text
NEEDS_APPROVAL
```

Meanwhile, the Internet and Netflix bills fall within the configured safety policy and are automatically processed.

After the autonomous workflow:

```text
Total Paid:          ₦32,000
Awaiting Approval:  ₦185,000
Blocked:             ₦0
```

After the user explicitly approves the Electricity bill:

```text
Total Paid:          ₦217,000
Awaiting Approval:   ₦0
Blocked:              ₦0
```

---

# 4. Key Features

## Autonomous Obligation Discovery

LifeOps discovers pending financial obligations from its task store and provides the agent with authoritative database task IDs.

The agent does not invent task identifiers.

---

## Historical Bill Investigation

Before making a decision, LifeOps retrieves historical payment information for each obligation.

This allows the system to identify unusual spending patterns rather than evaluating a bill using its current amount alone.

---

## Deterministic Policy Engine

Financial policy evaluation is implemented outside the LLM.

Current demo controls include:

```text
Automatic payment limit: ₦100,000
Outlier threshold:        30%
```

Possible decisions are:

```text
AUTO_HANDLE
NEEDS_APPROVAL
BLOCK
```

The agent must accept the policy result.

It cannot override it.

---

## Safe Automatic Payments

Bills classified as:

```text
AUTO_HANDLE
```

may proceed to the payment execution tool.

The payment layer independently checks the persisted decision before executing the transaction.

This means that even if an agent attempted to call the payment tool incorrectly, the payment controller would reject the request.

---

## Human-in-the-Loop Approval

Bills classified as:

```text
NEEDS_APPROVAL
```

cannot be automatically paid.

The dashboard presents the bill to the user for review.

The user must explicitly choose:

```text
Approve & Pay
```

before payment can proceed.

The AI agent cannot create an `APPROVED` decision on behalf of the human.

---

## Duplicate Payment Protection

LifeOps protects against duplicate execution.

Before processing a payment, the payment layer checks whether:

- the task is already paid,
- a completed transaction already exists,
- the latest decision permits payment.

This makes payment execution idempotent and reduces the risk of duplicate financial transactions.

---

## Persistent Activity History

Agent decisions and payment events are persisted.

The dashboard displays a chronological activity history showing how LifeOps handled each obligation.

This provides an audit trail instead of presenting only the final result.

---

## Explainability

Each bill includes a detailed explainability view containing information such as:

- current bill amount,
- historical average,
- percentage difference,
- original agent decision,
- latest decision,
- human approval status,
- payment status,
- historical transactions.

This makes it possible to understand **why** LifeOps made a decision.

---

## LifeOps Intelligence Panel

The dashboard summarizes the current financial state and identifies whether attention is required.

Example states include:

```text
HEALTHY
ATTENTION REQUIRED
```

This allows the user to quickly understand whether LifeOps has completed all obligations or requires human intervention.

---

## API Health Monitoring

The dashboard continuously monitors the FastAPI backend.

The system indicator displays whether the LifeOps API is:

```text
Online
Offline
Checking
```

---

# 5. Architecture

LifeOps uses a layered architecture.

```text
                         ┌─────────────────────┐
                         │       User          │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ LifeOps Dashboard   │
                         │ HTML / CSS / JS     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │      Strands Agent           │
                    │                               │
                    │  Amazon Bedrock               │
                    │  Claude Sonnet                │
                    └──────────────┬────────────────┘
                                   │
                 ┌─────────────────┼───────────────────┐
                 │                 │                   │
                 ▼                 ▼                   ▼
        ┌────────────────┐ ┌────────────────┐ ┌────────────────┐
        │ Task Discovery │ │ Bill History   │ │ Policy Engine  │
        └────────────────┘ └────────────────┘ └────────┬───────┘
                                                       │
                                      ┌────────────────┼───────────────┐
                                      │                │               │
                                      ▼                ▼               ▼
                               AUTO_HANDLE     NEEDS_APPROVAL        BLOCK
                                      │                │               │
                                      ▼                ▼               X
                              Persist Decision    Human Review
                                      │                │
                                      ▼                ▼
                              Payment Controller  Approve & Pay
                                      │                │
                                      └────────┬───────┘
                                               ▼
                                         SQLite State
                                               │
                                               ▼
                                      Activity / Reporting
```

---

# 6. AWS Architecture

LifeOps also runs as a deployed cloud agent using **Amazon Bedrock AgentCore Runtime**.

```text
LifeOps Agent
     │
     ▼
Strands Agents SDK
     │
     ▼
Amazon Bedrock
     │
     ▼
Amazon Bedrock AgentCore Runtime
     │
     ├── Runtime execution
     │
     ├── Session handling
     │
     └── Observability
             │
             ▼
        Amazon CloudWatch
```

The deployed AgentCore implementation demonstrates that the LifeOps agent can operate beyond the local development environment.

The deployed runtime has been successfully invoked with the complete LifeOps workflow.

AgentCore observability provides trace visibility for runtime executions.

---

# 7. Agent Tool Chain

The Strands agent works through a controlled tool chain.

```text
get_upcoming_tasks
        │
        ▼
get_bill_history
        │
        ▼
evaluate_bill_policy
        │
        ▼
record_decision
        │
        ▼
execute_payment
        │
        ▼
generate_financial_report
```

Each tool has a clearly defined responsibility.

### `get_upcoming_tasks`

Retrieves pending obligations and their authoritative task IDs.

### `get_bill_history`

Retrieves previous bill amounts for historical analysis.

### `evaluate_bill_policy`

Applies deterministic financial safety rules.

### `record_decision`

Persists the policy decision before financial execution.

### `execute_payment`

Executes only transactions permitted by persisted policy state.

### `generate_financial_report`

Produces the final financial summary after all obligations have been processed.

---

# 8. Sequential Financial Safety

One important design decision in LifeOps is that financial mutations are performed sequentially.

Read-only operations such as:

```text
history retrieval
policy evaluation
```

may be performed concurrently.

However:

```text
record decision
        ↓
wait for persistence
        ↓
execute payment
```

must occur sequentially.

This prevents race conditions where payment execution could occur before the corresponding decision has been committed.

The payment tool independently verifies the persisted decision before allowing execution.

---

# 9. Safety Model

LifeOps uses multiple layers of protection.

### Layer 1 — Deterministic policy

The LLM does not determine financial limits.

The policy engine does.

### Layer 2 — Persisted decisions

A decision must exist before payment execution.

### Layer 3 — Payment authorization

The payment tool independently validates the latest decision.

### Layer 4 — Human approval

`NEEDS_APPROVAL` transactions require explicit human intervention.

### Layer 5 — Duplicate protection

Previously completed payments cannot be executed again.

### Layer 6 — Audit history

Decisions and transactions are persisted for inspection.

This means safety does not depend solely on prompting the LLM to behave correctly.

---

# 10. Technology Stack

| Layer | Technology |
|---|---|
| Agent Framework | Strands Agents |
| Foundation Model | Amazon Bedrock |
| Model | Claude Sonnet |
| Cloud Agent Runtime | Amazon Bedrock AgentCore |
| Observability | Amazon CloudWatch / AgentCore Traces |
| Backend | FastAPI |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |
| Language | Python |
| Testing | Pytest |
| AWS Infrastructure | AWS CDK / AgentCore CLI |

---

# 11. Project Structure

A simplified representation of the repository:

```text
LIFEOPS/
│
├── agent/
│   └── orchestrator.py
│
├── api/
│   ├── main.py
│   ├── activity.py
│   ├── bill_details.py
│   └── ...
│
├── dashboard/
│   ├── index.html
│   ├── styles.css
│   └── app.js
│
├── database/
│   └── lifeops.db
│
├── tools/
│   ├── tasks.py
│   ├── policy.py
│   ├── payments.py
│   ├── investigation.py
│   ├── reporting.py
│   ├── approval.py
│   └── status.py
│
├── tests/
│   ├── test_api.py
│   └── test_payments.py
│
├── LifeOpsAgent/
│   ├── app/
│   │   └── LifeOpsAgent/
│   │       ├── main.py
│   │       ├── model/
│   │       ├── lifeops_tools/
│   │       └── pyproject.toml
│   │
│   └── agentcore/
│
├── reset_db.py
└── README.md
```

---

# 12. Local Installation

## Prerequisites

Recommended environment:

```text
Python 3.10+
AWS CLI
AWS credentials with Amazon Bedrock access
```

The project was developed and tested using Python 3.14.

Clone the repository:

```bash
git clone <YOUR_REPOSITORY_URL>
cd LIFEOPS
```

Create a virtual environment:

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project's Python dependencies using the dependency file included in the repository.

For example, if using `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

# 13. AWS Configuration

LifeOps uses Amazon Bedrock for agent reasoning.

Configure AWS credentials using the AWS CLI:

```bash
aws configure
```

Or use a named AWS profile.

Example:

```powershell
$env:AWS_PROFILE = "lifeops"
$env:AWS_REGION = "us-east-1"
```

Verify the active AWS identity:

```bash
aws sts get-caller-identity
```

> Do not commit AWS access keys, secret keys, session tokens, `.env` credentials, or other secrets to the repository.

---

# 14. Running LifeOps Locally

From the repository root:

```bash
uvicorn api.main:app --reload
```

The FastAPI server will start locally.

Open:

```text
http://127.0.0.1:8000/
```

The LifeOps dashboard is served directly by FastAPI.

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

---

# 15. Running the Demo

For a clean demonstration, reset the local database:

```bash
python reset_db.py
```

Expected starting state:

```text
Electricity Bill       → pending
Internet Subscription  → pending
Netflix                → pending

Agent decisions: 0
Payments:        0
```

Start the application:

```bash
uvicorn api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

Click:

```text
Run LifeOps
```

The Strands agent will:

```text
1. Discover pending obligations
2. Retrieve historical bill information
3. Evaluate deterministic policy
4. Persist each decision
5. Automatically pay safe obligations
6. Escalate unsafe/high-value obligations
7. Generate the final financial report
```

Expected result:

```text
Electricity Bill       → NEEDS_APPROVAL
Internet Subscription  → PAID
Netflix                → PAID

Total Paid:          ₦32,000
Awaiting Approval:  ₦185,000
Blocked:             ₦0
```

Review the Electricity bill and select:

```text
Approve & Pay
```

Expected final state:

```text
Electricity Bill       → PAID
Internet Subscription  → PAID
Netflix                → PAID

Total Paid:          ₦217,000
Awaiting Approval:   ₦0
Blocked:             ₦0
```

---

# 16. Important API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | LifeOps dashboard |
| GET | `/health` | API health check |
| GET | `/api/dashboard` | Dashboard state |
| GET | `/api/bills` | Retrieve bills |
| GET | `/api/bill/{bill_name}` | Bill status |
| GET | `/api/bill/{bill_name}/details` | Explainability/details |
| POST | `/api/bill/{bill_name}/approve` | Human approval |
| POST | `/api/bill/{bill_name}/pay` | Execute permitted payment |
| POST | `/api/run` | Run LifeOps autonomous workflow |
| GET | `/api/activity` | Persistent activity history |

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# 17. Running Tests

Run:

```bash
python -m pytest -v
```

Current verified test result:

```text
10 passed
```

The automated test suite covers important behaviours including:

```text
API health
bill status retrieval
unknown bill handling
dashboard endpoint
approval restrictions
approved payment execution
payment idempotency
NEEDS_APPROVAL payment blocking
BLOCK payment blocking
AUTO_HANDLE payment execution
```

---

# 18. AgentCore Deployment

LifeOps includes an AgentCore-compatible application under:

```text
LifeOpsAgent/
```

The AgentCore application uses the same core LifeOps safety model while maintaining isolated demonstration state for cloud runtime validation.

This cloud demonstration is intentionally separate from the local SQLite-backed dashboard state.

The local application remains the primary end-to-end product experience.

## AgentCore prerequisites

The project uses:

```text
AWS CLI
Node.js
AWS CDK
AgentCore CLI
uv
```

Install the AgentCore CLI:

```bash
npm install -g @aws/agentcore
```

Verify:

```bash
agentcore --version
```

---

# 19. Running AgentCore Locally

Navigate to:

```text
LifeOpsAgent/
```

Start the AgentCore development runtime:

```bash
agentcore dev --port 8080 --logs
```

From another terminal:

```bash
agentcore dev "run lifeops" --stream
```

The expected result mirrors the autonomous portion of the LifeOps workflow:

```text
Internet Subscription → AUTO_HANDLE → PAID
Netflix               → AUTO_HANDLE → PAID
Electricity Bill      → NEEDS_APPROVAL
```

---

# 20. Deploying to Amazon Bedrock AgentCore

Before deploying, verify the AWS account and region carefully:

```bash
aws sts get-caller-identity
```

Perform a deployment dry run:

```bash
agentcore deploy --dry-run
```

When ready:

```bash
agentcore deploy
```

Check deployment status:

```bash
agentcore status
```

A successful deployment should report the runtime as:

```text
READY
```

Invoke the deployed agent:

```bash
agentcore invoke --prompt "run lifeops" --stream
```

---

# 21. AgentCore Observability

LifeOps emits runtime telemetry through AgentCore observability.

Runtime logs can be viewed using:

```bash
agentcore logs
```

Agent traces can be listed using:

```bash
agentcore traces list
```

These traces provide evidence of cloud agent execution and can be inspected through Amazon CloudWatch.

This is particularly important for autonomous systems because it provides visibility into how the agent behaves during execution.

---

# 22. Local State vs AgentCore Demo State

The repository currently contains two execution environments.

### Local LifeOps

The local FastAPI/dashboard application uses:

```text
SQLite
```

as its authoritative state store.

This provides the complete end-to-end experience including:

- dashboard,
- persistent activity,
- human approval,
- payment state,
- explainability.

### AgentCore Runtime

The AgentCore deployment uses isolated demonstration state packaged with the cloud agent.

This was deliberately chosen to validate:

- Strands orchestration,
- Amazon Bedrock reasoning,
- AgentCore Runtime,
- cloud invocation,
- observability,

without introducing a second shared cloud database into the hackathon prototype.

Therefore, the AgentCore demo should **not** be interpreted as sharing live SQLite state with the local dashboard.

A production version could replace these stores with a shared managed persistence layer.

---

# 23. Current Prototype Limitations

LifeOps is a hackathon prototype and does not currently move real money.

Payment execution is simulated through the application's payment transaction layer.

A production implementation would require integration with regulated payment providers and additional controls including:

- authentication,
- authorization,
- encrypted secret management,
- transaction signing,
- fraud detection,
- provider webhooks,
- reconciliation,
- regulatory compliance,
- stronger persistent cloud storage,
- user-specific policy configuration,
- production-grade audit retention.

The current prototype focuses on demonstrating the **agent architecture, autonomous workflow, deterministic safety controls, human-in-the-loop design, and cloud agent deployment**.

---

# 24. Production Evolution

A production LifeOps architecture could evolve toward:

```text
Bank / Billing APIs
        │
        ▼
Event / Obligation Detection
        │
        ▼
Strands Agent
        │
        ▼
Amazon Bedrock
        │
        ▼
Deterministic Policy Engine
        │
        ├── Safe ─────────► Payment Provider
        │
        ├── Review ───────► Human Approval
        │
        └── Block ────────► Security / Audit
        │
        ▼
Shared Cloud Database
        │
        ▼
AgentCore Runtime
        │
        ▼
CloudWatch Observability
```

Potential future capabilities include:

- bank account integrations,
- utility provider integrations,
- recurring obligation discovery,
- configurable user spending policies,
- anomaly detection,
- budget-aware decision making,
- notification services,
- multi-user authentication,
- shared cloud persistence,
- mobile applications,
- transaction reconciliation.

---

# 25. Why Use an AI Agent?

A traditional automation could simply implement:

```text
if amount < limit:
    pay()
```

LifeOps goes beyond this.

The agent coordinates multiple pieces of information and tools across a workflow:

```text
What obligations exist?
        ↓
What happened previously?
        ↓
Is the current amount unusual?
        ↓
What does financial policy permit?
        ↓
Should this be automated or escalated?
        ↓
Was the decision persisted?
        ↓
Can payment safely execute?
        ↓
What happened across all obligations?
```

The LLM is valuable for **reasoning and orchestration**.

Deterministic software remains responsible for **financial authorization and enforcement**.

This separation is central to the LifeOps architecture.

---

# 26. Design Philosophy

LifeOps is built around three principles.

### Autonomous where safe

Routine obligations should not constantly require human attention.

### Human where necessary

High-risk, unusual, or high-value transactions should surface to the user.

### Deterministic where critical

Sensitive financial execution should never depend solely on probabilistic LLM output.

Together, these principles create:

> **Bounded autonomy — giving AI enough authority to be useful without giving it enough authority to become unsafe.**

---

# 27. Hackathon Highlights

LifeOps demonstrates:

**Strands Agents**

Used as the primary autonomous orchestration layer.

**Amazon Bedrock**

Provides the model reasoning behind the agent.

**Amazon Bedrock AgentCore**

Hosts the deployed cloud agent runtime.

**AgentCore Observability**

Provides runtime trace visibility through CloudWatch.

**Deterministic Financial Safety**

Critical payment authorization remains outside the LLM.

**Human-in-the-Loop Control**

High-value or anomalous obligations require explicit approval.

**Explainable Decisions**

Users can inspect historical information and understand why an obligation was escalated.

**End-to-End Product Experience**

The project includes an API, database, autonomous agent, safety controls, dashboard, human approval workflow, activity history, explainability, automated testing, and cloud deployment.

---

# 28. Verified Project Status

The current LifeOps build has been verified through:

```text
✓ Clean database reset
✓ Dashboard startup
✓ API health monitoring
✓ Three-bill autonomous workflow
✓ Historical bill analysis
✓ Deterministic policy enforcement
✓ Safe automatic payments
✓ High-value transaction escalation
✓ Human approval workflow
✓ Duplicate-payment protection
✓ Persistent activity history
✓ Explainability views
✓ State persistence after browser refresh
✓ 10/10 automated tests
✓ Strands + Amazon Bedrock execution
✓ AgentCore local runtime execution
✓ AgentCore cloud deployment
✓ AgentCore runtime READY
✓ Successful cloud invocation
✓ CloudWatch / AgentCore trace visibility
```

---

# 29. Final Result

LifeOps demonstrates a practical model for autonomous financial agents:

> **Reason with AI. Enforce with deterministic controls. Escalate to humans when risk requires it.**

The goal is not to remove humans from financial decision-making.

The goal is to remove humans from routine financial work while ensuring they remain in control when their judgment matters most.

---

## Built With

**Strands Agents · Amazon Bedrock · Amazon Bedrock AgentCore · FastAPI · SQLite · Python · JavaScript · AWS CloudWatch**

---

## Disclaimer

LifeOps is currently a prototype created for demonstration and hackathon purposes.

It does not process real financial transactions and should not be used as a production financial system without appropriate security, regulatory, payment-provider, authentication, and operational controls.
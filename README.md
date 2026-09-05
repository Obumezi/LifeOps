# LifeOps

> **An autonomous AI agent for managing routine financial obligations safely, escalating only when human judgment is required.**

### 🚀 [Launch the Live Demo](https://lifeops-qyit.onrender.com/)

**Live Demo:** https://lifeops-qyit.onrender.com/

**Repository:** https://github.com/Obumezi/LifeOps

LifeOps is an AI-powered financial operations agent built with **Strands Agents, Amazon Bedrock, Amazon Bedrock AgentCore, FastAPI, SQLite, Python, and JavaScript**.

Instead of simply reminding a user that a bill is due, LifeOps investigates the obligation, reviews historical spending, evaluates deterministic safety policies, decides whether the obligation can be handled automatically, executes permitted simulated payments, and escalates unusual or high-value transactions for human approval.

The project demonstrates **bounded AI autonomy**:

> **AI can reason and orchestrate workflows, but it cannot override deterministic financial controls.**

---

# Quick Start for Judges and Reviewers

The fastest way to experience LifeOps is through the public demo:

### [Open the LifeOps Live Demo](https://lifeops-qyit.onrender.com/)

For local reproduction:

```bash
git clone https://github.com/Obumezi/LifeOps.git
cd LifeOps

python -m venv .venv
```

Activate the virtual environment.

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your own AWS credentials and verify them:

```bash
aws sts get-caller-identity
```

Reset the LifeOps demo:

```bash
python reset_db.py
```

Start the application:

```bash
uvicorn api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

Then click:

```text
Run LifeOps
```

Expected autonomous result:

```text
Electricity Bill       → NEEDS_APPROVAL
Internet Subscription  → PAID
Netflix                → PAID
```

Review the Electricity Bill, approve it, and the final state should show:

```text
3/3 obligations resolved
Total Paid: ₦217,000
Awaiting Approval: ₦0
Blocked: ₦0
```

> Reviewers must use their own AWS credentials. No developer passwords, IAM credentials, access keys, or AWS account access are required.

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

This makes LifeOps a strong fit for the **Everyday Agents** category: routine financial busywork can be handled autonomously, while the user is brought back into the loop only when a meaningful decision is required.

---

# 2. Core Idea

LifeOps follows one central principle:

> **AI decides what should happen. Deterministic controls decide what is allowed to happen.**

The Strands agent orchestrates the workflow.

It can:

- discover pending obligations,
- retrieve historical bill information,
- request deterministic policy evaluation,
- persist decisions,
- initiate permitted payments,
- generate financial reports.

However, the LLM does **not** have unrestricted authority to execute payments.

Financial actions are protected by deterministic tools and policies.

```text
Current Bill
     │
     ▼
Historical Analysis
     │
     ▼
Deterministic Policy Evaluation
     │
     ├── AUTO_HANDLE ───────► Payment permitted
     │
     ├── NEEDS_APPROVAL ────► Human approval required
     │
     └── BLOCK ─────────────► Payment prohibited
```

This creates a bounded-autonomy architecture where AI provides intelligence and orchestration without becoming the final authority over sensitive financial actions.

---

# 3. Demo Scenario

LifeOps demonstrates the workflow using three financial obligations.

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

Difference from historical average:

```text
≈ +44.91%
```

Automatic-payment limit:

```text
₦100,000
```

LifeOps therefore refuses to automatically process the Electricity Bill.

The deterministic policy returns:

```text
NEEDS_APPROVAL
```

Meanwhile, the Internet and Netflix obligations fall within the configured safety policy and are automatically processed.

After the autonomous workflow:

```text
Total Paid:          ₦32,000
Awaiting Approval:  ₦185,000
Blocked:             ₦0
```

After the user explicitly approves the Electricity Bill:

```text
Total Paid:          ₦217,000
Awaiting Approval:   ₦0
Blocked:             ₦0
Resolved:            3/3
```

---

# 4. Key Features

## Autonomous Obligation Discovery

LifeOps discovers pending financial obligations from its task store and provides the agent with authoritative task IDs.

The agent does not invent identifiers.

---

## Historical Bill Investigation

Before making a decision, LifeOps retrieves previous bill amounts.

This allows the system to evaluate whether the current bill is consistent with the user's historical spending pattern.

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

The Strands agent must respect the policy result.

It cannot override it.

---

## Safe Automatic Payments

Bills classified as:

```text
AUTO_HANDLE
```

may proceed to the payment execution layer.

The payment layer independently checks the persisted decision before processing a transaction.

This means that even if an agent attempted to call the payment tool incorrectly, the payment controller would reject the request.

---

## Human-in-the-Loop Approval

Bills classified as:

```text
NEEDS_APPROVAL
```

cannot be automatically processed.

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

Payment execution is therefore designed to be idempotent.

---

## Persistent Activity History

Agent decisions and payment events are persisted.

The dashboard displays a chronological history showing how each obligation was handled.

---

## Explainability

Each bill includes an explainability view containing information such as:

- current bill amount,
- historical average,
- percentage difference,
- original agent decision,
- latest decision,
- human approval status,
- payment status,
- historical transactions.

This allows users to understand **why** the agent made a particular decision.

---

## LifeOps Intelligence Panel

The dashboard summarizes the user's financial-operation state.

Example states include:

```text
HEALTHY
ATTENTION REQUIRED
```

This allows the user to immediately see whether LifeOps requires human intervention.

---

## API Health Monitoring

The dashboard monitors the FastAPI backend.

The interface displays:

```text
Online
Offline
Checking
```

---

# 5. Architecture

## Architecture Diagram

![LifeOps Architecture](docs/lifeops-architecture.png)

LifeOps uses a layered architecture.

```text
                         ┌─────────────────────┐
                         │        User         │
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
                   ┌────────────────┴──────────────┐
                   │                               │
                   ▼                               ▼
          ┌─────────────────┐             ┌─────────────────┐
          │  SQLite State   │             │  Strands Agent  │
          └─────────────────┘             └────────┬────────┘
                                                   │
                                                   ▼
                                          ┌─────────────────┐
                                          │ Amazon Bedrock  │
                                          │ Claude Sonnet   │
                                          └────────┬────────┘
                                                   │
                                                   ▼
                                      ┌────────────────────────┐
                                      │ Controlled Agent Tools │
                                      └───────────┬────────────┘
                                                  │
                      ┌───────────────────────────┼─────────────────────────┐
                      │                           │                         │
                      ▼                           ▼                         ▼
               Task Discovery              Bill History               Policy Engine
                                                  │
                                                  ▼
                                    AUTO_HANDLE / NEEDS_APPROVAL / BLOCK
                                                  │
                                                  ▼
                                         Persist Decision
                                                  │
                               ┌──────────────────┴─────────────────┐
                               │                                    │
                               ▼                                    ▼
                       Payment Controller                    Human Review
                               │                                    │
                               └──────────────────┬─────────────────┘
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
     ├── Session handling
     └── Observability
             │
             ▼
        Amazon CloudWatch
```

The deployed AgentCore implementation demonstrates that LifeOps can execute outside the local development environment.

The deployed runtime has successfully executed the LifeOps autonomous workflow.

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

### `get_upcoming_tasks`

Retrieves pending obligations and authoritative task IDs.

### `get_bill_history`

Retrieves historical bill amounts.

### `evaluate_bill_policy`

Applies deterministic financial rules.

### `record_decision`

Persists the resulting policy decision.

### `execute_payment`

Processes only transactions permitted by persisted policy state.

### `generate_financial_report`

Produces a financial summary after the agent completes its workflow.

---

# 8. Sequential Financial Safety

Financial mutations are intentionally performed sequentially.

Read-only operations such as:

```text
history retrieval
policy evaluation
```

may occur independently.

However:

```text
record decision
        ↓
wait for persistence
        ↓
execute payment
```

must occur in order.

This prevents a payment from being processed before the corresponding decision has been persisted.

The payment tool also independently verifies the decision before allowing execution.

---

# 9. Safety Model

LifeOps uses multiple safety layers.

### Layer 1 — Deterministic Policy

The LLM does not determine financial limits.

The policy engine does.

### Layer 2 — Persisted Decisions

A valid decision must exist before payment execution.

### Layer 3 — Payment Authorization

The payment layer independently validates the latest decision.

### Layer 4 — Human Approval

`NEEDS_APPROVAL` transactions require explicit human intervention.

### Layer 5 — Duplicate Protection

Completed payments cannot be executed again.

### Layer 6 — Audit History

Decisions and payment events remain available for inspection.

Safety therefore does not depend solely on instructing the LLM to behave correctly.

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
| Infrastructure | AWS CDK / AgentCore |

---

# 11. Project Structure

```text
LifeOps/
│
├── agent/
│   ├── orchestrator.py
│   └── action_router.py
│
├── api/
│   ├── main.py
│   ├── activity.py
│   ├── bill_details.py
│   └── services.py
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
├── docs/
│   └── lifeops-architecture.png
│
├── LICENSE
├── requirements.txt
├── reset_db.py
└── README.md
```

---

# 12. Local Installation

## Prerequisites

Before running LifeOps locally, ensure you have:

- Python 3.10 or later
- Git
- AWS CLI
- An AWS account
- Amazon Bedrock access
- AWS credentials configured for your own AWS identity

LifeOps was developed and tested using Python 3.14.

> You do not need the developer's AWS credentials, IAM password, account alias, access keys, or AWS account login to reproduce LifeOps.

---

## Clone the Repository

```bash
git clone https://github.com/Obumezi/LifeOps.git
cd LifeOps
```

---

## Create a Virtual Environment

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 13. AWS Configuration

LifeOps uses Amazon Bedrock for agent reasoning through the Strands Agents SDK.

Anyone reproducing the project locally must authenticate using **their own AWS account and credentials**.

The repository does not contain the developer's AWS credentials.

---

## Required AWS Permissions

The AWS identity running LifeOps must have permission to invoke Amazon Bedrock models.

At minimum:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel",
        "bedrock:InvokeModelWithResponseStream"
      ],
      "Resource": "*"
    }
  ]
}
```

For production environments, permissions should be restricted further to only the required resources.

---

## AWS Region

LifeOps uses:

```text
us-east-1
```

Ensure the required Amazon Bedrock model is available to your AWS account in this region.

---

## Configure AWS Credentials

### Option 1 — AWS CLI Credentials

Run:

```bash
aws configure
```

Provide credentials for your own AWS IAM identity.

Set the default region to:

```text
us-east-1
```

---

### Option 2 — Named AWS Profile

Windows PowerShell:

```powershell
$env:AWS_PROFILE = "your-profile-name"
$env:AWS_REGION = "us-east-1"
```

macOS / Linux:

```bash
export AWS_PROFILE="your-profile-name"
export AWS_REGION="us-east-1"
```

The AWS profile name is local to your computer.

You do not need to create a profile named `lifeops`.

---

## Verify AWS Authentication

Before starting LifeOps:

```bash
aws sts get-caller-identity
```

A successful result should resemble:

```json
{
  "UserId": "EXAMPLEUSERID",
  "Account": "123456789012",
  "Arn": "arn:aws:iam::123456789012:user/example-user"
}
```

Your actual values will be different.

If this command fails, resolve AWS authentication before starting LifeOps.

> AWS root credentials are not recommended. Use an appropriately permissioned IAM identity.

---

## Expired AWS Sessions

Temporary credentials and AWS CLI login sessions can expire.

Symptoms may include:

```text
LoginRefreshRequired
```

or:

```text
The refresh token has expired
```

If your environment uses AWS CLI login, reauthenticate:

```bash
aws login
```

For a named profile:

```bash
aws login --profile your-profile-name
```

Then verify:

```bash
aws sts get-caller-identity
```

Restart LifeOps after authentication succeeds.

---

## Security Notice

Never commit AWS credentials to the repository.

Do not commit:

```text
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN
IAM passwords
AWS CLI credential files
.env
```

LifeOps' `.gitignore` excludes common local secret and environment files.

---

# 14. Running LifeOps Locally

First verify AWS authentication:

```bash
aws sts get-caller-identity
```

Reset the demo database:

```bash
python reset_db.py
```

Expected clean state:

```text
Electricity Bill       → pending
Internet Subscription  → pending
Netflix                → pending

Agent decisions: 0
Payments:        0
```

Start FastAPI:

```bash
uvicorn api.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

Health endpoint:

```text
http://127.0.0.1:8000/health
```

---

# 15. Reproducing the Demo

After opening the dashboard, confirm:

```text
System Status → Online

Electricity Bill       → Pending
Internet Subscription  → Pending
Netflix                → Pending
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
5. Automatically process safe obligations
6. Escalate high-risk obligations
7. Generate the final financial report
```

Expected autonomous result:

```text
Electricity Bill       → NEEDS_APPROVAL
Internet Subscription  → PAID
Netflix                → PAID
```

Expected summary:

```text
Total Paid:          ₦32,000
Awaiting Approval:  ₦185,000
Blocked:             ₦0
```

The Electricity Bill is escalated because:

```text
Current amount:         ₦185,000
Historical average:     ≈ ₦127,666.67
Difference:             ≈ 44.91%
Automatic payment cap:  ₦100,000
```

Review the Electricity Bill and select:

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

Resolved: 3/3
```

> Payment execution in this prototype is simulated. No real money is transferred.

---

# 16. Important API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | LifeOps dashboard |
| GET | `/health` | API health check |
| GET | `/api/dashboard` | Dashboard state |
| GET | `/api/bills` | Retrieve bills |
| GET | `/api/bill/{bill_name}` | Bill status |
| GET | `/api/bill/{bill_name}/details` | Explainability details |
| POST | `/api/bill/{bill_name}/approve` | Human approval |
| POST | `/api/bill/{bill_name}/pay` | Execute permitted payment |
| POST | `/api/run` | Run LifeOps autonomous workflow |
| GET | `/api/activity` | Activity history |

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

Current verified result:

```text
10 passed
```

The tests cover:

- API health
- bill status retrieval
- unknown bill handling
- dashboard endpoint
- approval restrictions
- approved payment execution
- payment idempotency
- `NEEDS_APPROVAL` payment blocking
- `BLOCK` payment blocking
- `AUTO_HANDLE` payment execution

---

# 18. Troubleshooting

## `Run LifeOps` Returns `500 Internal Server Error`

First verify AWS authentication:

```bash
aws sts get-caller-identity
```

If authentication fails or has expired, reauthenticate.

Then restart:

```bash
uvicorn api.main:app --reload
```

---

## `LoginRefreshRequired`

This usually means the AWS authentication session expired.

Reauthenticate:

```bash
aws login
```

or:

```bash
aws login --profile your-profile-name
```

Verify:

```bash
aws sts get-caller-identity
```

Then restart the application.

---

## `AccessDeniedException`

Confirm your AWS identity has:

```text
bedrock:InvokeModel
bedrock:InvokeModelWithResponseStream
```

Also confirm that the required Bedrock model is available in:

```text
us-east-1
```

---

## Dashboard Shows Old Payment State After Reset

Run:

```bash
python reset_db.py
```

Then hard-refresh the browser.

Expected reset state:

```text
Electricity → pending
Internet    → pending
Netflix     → pending
```

You can verify the backend directly with:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/dashboard | ConvertTo-Json -Depth 10
```

---

## Verify Backend Health

Open:

```text
http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "healthy",
  "service": "LifeOps"
}
```

---

# 19. Public Demo

A hosted version of LifeOps is available here:

### [Launch LifeOps](https://lifeops-qyit.onrender.com/)

The public demo allows reviewers to experience LifeOps without configuring a local AWS development environment.

> The hosted service may require a short startup period after inactivity.

The public deployment uses restricted AWS credentials configured on the hosting platform. These credentials are not included in the repository.

---

# 20. Amazon Bedrock AgentCore Deployment

LifeOps includes an AgentCore-compatible application under:

```text
LifeOpsAgent/
```

The AgentCore application uses the same core LifeOps safety model while maintaining isolated demonstration state for cloud runtime validation.

This cloud demonstration is intentionally separate from the local SQLite-backed dashboard state.

The local FastAPI application remains the primary end-to-end product experience.

---

## AgentCore Prerequisites

AgentCore deployment requires an AWS environment with the appropriate AgentCore permissions and supporting tools, including:

```text
AWS CLI
Node.js
AWS CDK
uv
AgentCore CLI
```

Verify:

```bash
agentcore --version
```

and:

```bash
uv --version
```

---

# 21. Running AgentCore Locally

Navigate to:

```text
LifeOpsAgent/
```

Start the local AgentCore runtime:

```bash
agentcore dev --port 8080 --logs
```

From another terminal:

```bash
agentcore dev "run lifeops" --stream
```

Expected result:

```text
Internet Subscription → AUTO_HANDLE → PAID
Netflix               → AUTO_HANDLE → PAID
Electricity Bill      → NEEDS_APPROVAL
```

---

# 22. Deploying to Amazon Bedrock AgentCore

Verify AWS identity:

```bash
aws sts get-caller-identity
```

Perform a dry run:

```bash
agentcore deploy --dry-run
```

If AWS CDK bootstrap is required, complete the bootstrap for your own AWS account and deployment region.

Deploy:

```bash
agentcore deploy
```

Check deployment:

```bash
agentcore status
```

A successful deployment should report:

```text
Runtime: READY
```

Invoke the deployed agent:

```bash
agentcore invoke --prompt "run lifeops" --stream
```

---

# 23. AgentCore Observability

Stream runtime logs:

```bash
agentcore logs
```

List traces:

```bash
agentcore traces list
```

AgentCore observability and Amazon CloudWatch provide visibility into deployed agent execution.

This is particularly important for autonomous systems because it provides operational traceability beyond the final response shown to the user.

---

# 24. Local State vs AgentCore Demo State

LifeOps contains two execution environments.

## Local LifeOps

The FastAPI/dashboard application uses:

```text
SQLite
```

as its authoritative demo state store.

It provides:

- dashboard state,
- decisions,
- human approval,
- simulated payment state,
- activity history,
- explainability.

## AgentCore Runtime

The AgentCore deployment uses isolated demo state packaged with the cloud agent.

It validates:

- Strands orchestration,
- Amazon Bedrock reasoning,
- AgentCore Runtime,
- cloud invocation,
- observability.

The AgentCore runtime does **not** share the local SQLite database.

This separation is intentional for the hackathon prototype.

---

# 25. Current Prototype Limitations

LifeOps is a hackathon prototype.

It does not move real money.

Payment execution is simulated through the application transaction layer.

A production version would require:

- regulated payment-provider integrations,
- authentication,
- authorization,
- encrypted secret management,
- transaction signing,
- fraud detection,
- provider webhooks,
- reconciliation,
- regulatory compliance,
- managed cloud persistence,
- configurable user policy,
- production-grade audit retention.

The current prototype focuses on demonstrating:

- agent architecture,
- autonomous workflows,
- deterministic financial safety,
- human-in-the-loop control,
- explainability,
- cloud deployment,
- observability.

---

# 26. Production Evolution

A future LifeOps architecture could evolve toward:

```text
Bank / Billing APIs
        │
        ▼
Obligation Detection
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

Potential capabilities include:

- bank integrations,
- utility-provider integrations,
- recurring obligation discovery,
- configurable spending policies,
- anomaly detection,
- budget-aware decision making,
- notification services,
- adaptive policy recommendations,
- multi-user authentication,
- shared cloud persistence,
- mobile applications,
- transaction reconciliation.

An important future design principle would remain unchanged:

> The agent may recommend changes to financial safety rules, but it should not be able to independently rewrite the safeguards that constrain it.

---

# 27. Why Use an AI Agent?

A simple automation could implement:

```python
if amount < limit:
    pay()
```

LifeOps goes beyond a fixed conditional.

The agent coordinates multiple pieces of information and tools:

```text
What obligations exist?
        ↓
What happened previously?
        ↓
Is the current amount unusual?
        ↓
What does policy permit?
        ↓
Should the transaction be automated or escalated?
        ↓
Was the decision persisted?
        ↓
Can payment safely execute?
        ↓
What happened across all obligations?
```

The LLM is useful for:

```text
Reasoning
Orchestration
Tool selection
Workflow coordination
```

Deterministic software remains responsible for:

```text
Policy enforcement
Financial authorization
Duplicate protection
Human approval boundaries
```

This separation is central to LifeOps.

---

# 28. Design Philosophy

LifeOps is built around three principles.

### Autonomous Where Safe

Routine obligations should not constantly require human attention.

### Human Where Necessary

High-risk, unusual, or high-value transactions should surface to the user.

### Deterministic Where Critical

Sensitive financial execution should never depend solely on probabilistic LLM output.

Together, these principles create:

> **Bounded autonomy — giving AI enough authority to be useful without giving it enough authority to become unsafe.**

---

# 29. Hackathon Highlights

### Strands Agents

Used as the primary autonomous orchestration layer.

### Amazon Bedrock

Provides model reasoning for the agent.

### Amazon Bedrock AgentCore

Hosts the deployed cloud agent runtime.

### AgentCore Observability

Provides runtime trace visibility through Amazon CloudWatch.

### Deterministic Financial Safety

Critical payment authorization remains outside the LLM.

### Human-in-the-Loop Control

High-value or anomalous obligations require explicit approval.

### Explainable Decisions

Users can inspect historical data and understand why an obligation was escalated.

### Public Live Demo

Reviewers can experience LifeOps without configuring a local development environment.

### End-to-End Product Experience

LifeOps includes:

- autonomous agent,
- API,
- database,
- dashboard,
- safety controls,
- human approval,
- activity history,
- explainability,
- automated testing,
- public deployment,
- AgentCore deployment,
- cloud observability.

---

# 30. Verified Project Status

The current LifeOps build has been verified through:

```text
✓ Clean database reset
✓ Dashboard startup
✓ Public live dashboard
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
✓ Public Render deployment
✓ Public Render → Amazon Bedrock execution
✓ End-to-end public human approval workflow
```

---

# 31. Final Result

LifeOps demonstrates a practical model for autonomous financial agents:

> **Reason with AI. Enforce with deterministic controls. Escalate to humans when risk requires it.**

The goal is not to remove humans from financial decision-making.

The goal is to remove humans from repetitive financial busywork while ensuring they remain in control whenever judgment genuinely matters.

---

# License

LifeOps is released under the **MIT License**.

See:

```text
LICENSE
```

for the complete license terms.

---

# Built With

**Strands Agents · Amazon Bedrock · Amazon Bedrock AgentCore · FastAPI · SQLite · Python · JavaScript · AWS CloudWatch**

---

# Disclaimer

LifeOps is a prototype created for demonstration and hackathon purposes.

It does not process real financial transactions.

It should not be used as a production financial system without appropriate security, authentication, payment-provider integration, regulatory controls, infrastructure, and operational safeguards.
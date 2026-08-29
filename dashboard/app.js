const API = "/api";

let pendingApproval = null;


/* ============================================================
   UTILITIES
   ============================================================ */

function formatMoney(amount, currency = "NGN") {
    return new Intl.NumberFormat(
        "en-NG",
        {
            style: "currency",
            currency: currency || "NGN",
            maximumFractionDigits: 0
        }
    ).format(Number(amount || 0));
}


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function showToast(message) {
    const toast = document.getElementById("toast");

    if (!toast) {
        return;
    }

    toast.textContent =
        message || "LifeOps action completed";

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);
}


function formatDetailDate(value) {
    if (!value) {
        return "—";
    }

    let date;

    /*
     * SQLite timestamps look like:
     * 2026-08-29 16:51:39
     *
     * Bill history dates look like:
     * 2026-05-28
     */

    if (
        String(value).includes(" ") &&
        !String(value).includes("T")
    ) {
        date = new Date(
            String(value).replace(" ", "T")
        );
    } else if (
        /^\d{4}-\d{2}-\d{2}$/.test(
            String(value)
        )
    ) {
        date = new Date(
            `${value}T00:00:00`
        );
    } else {
        date = new Date(value);
    }

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat(
        "en-NG",
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    ).format(date);
}


function formatActivityTime(value) {
    if (!value) {
        return "";
    }

    const normalized =
        String(value).includes("T")
            ? String(value)
            : String(value).replace(" ", "T");

    const date = new Date(normalized);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return date.toLocaleString(
        "en-NG",
        {
            day: "2-digit",
            month: "short",
            hour: "2-digit",
            minute: "2-digit"
        }
    );
}


/* ============================================================
   BILL STATUS
   ============================================================ */

function getStatusBadge(bill) {
    if (
        bill.status === "paid" &&
        bill.payment_status === "COMPLETED"
    ) {
        return `
            <span class="badge badge-paid">
                PAID
            </span>
        `;
    }

    if (
        bill.decision === "NEEDS_APPROVAL"
    ) {
        return `
            <span class="badge badge-approval">
                AWAITING APPROVAL
            </span>
        `;
    }

    if (
        bill.decision === "BLOCK" ||
        bill.decision === "BLOCKED"
    ) {
        return `
            <span class="badge badge-blocked">
                BLOCKED
            </span>
        `;
    }

    return `
        <span class="badge badge-pending">
            PENDING
        </span>
    `;
}


/* ============================================================
   DECISION BADGES
   ============================================================ */

function getDecisionBadge(bill) {
    const decision = bill.decision;

    if (!decision) {
        return `
            <span class="badge badge-pending">
                NO DECISION
            </span>
        `;
    }

    if (decision === "AUTO_HANDLE") {
        return `
            <span class="badge badge-paid">
                AUTO HANDLE
            </span>
        `;
    }

    if (decision === "APPROVED") {
        return `
            <span class="badge badge-paid">
                APPROVED
            </span>
        `;
    }

    if (decision === "NEEDS_APPROVAL") {
        return `
            <span class="badge badge-approval">
                NEEDS APPROVAL
            </span>
        `;
    }

    if (
        decision === "BLOCK" ||
        decision === "BLOCKED"
    ) {
        return `
            <span class="badge badge-blocked">
                BLOCKED
            </span>
        `;
    }

    return `
        <span class="badge badge-pending">
            ${escapeHtml(decision)}
        </span>
    `;
}


/* ============================================================
   BILL ACTIONS
   ============================================================ */

function getActions(bill) {
    const encodedName =
        encodeURIComponent(bill.name);

    /*
     * Already paid.
     */

    if (
        bill.status === "paid" &&
        bill.payment_status === "COMPLETED"
    ) {
        return `
            <span class="badge badge-paid">
                Completed
            </span>
        `;
    }

    /*
     * Human review required.
     */

    if (
        bill.decision === "NEEDS_APPROVAL"
    ) {
        const amount =
            Number(bill.amount || 0);

        const reason =
            bill.reason ||
            bill.decision_reason ||
            "This payment exceeds LifeOps automatic payment safety limits.";

        return `
            <div class="action-group">

                <button
                    class="action-button approve"
                    type="button"
                    onclick="openApprovalModal(
                        '${encodedName}',
                        ${amount},
                        '${encodeURIComponent(reason)}'
                    )"
                >
                    Review
                </button>

            </div>
        `;
    }

    /*
     * Approved or automatically cleared.
     */

    if (
        bill.decision === "AUTO_HANDLE" ||
        bill.decision === "APPROVED"
    ) {
        return `
            <div class="action-group">

                <button
                    class="action-button pay"
                    type="button"
                    onclick="payBill('${encodedName}')"
                >
                    Pay
                </button>

            </div>
        `;
    }

    return `
        <span class="badge badge-pending">
            No action
        </span>
    `;
}


/* ============================================================
   RENDER BILLS
   ============================================================ */

function renderBills(bills) {
    const table =
        document.getElementById("billsTable");

    if (!table) {
        return;
    }

    if (
        !Array.isArray(bills) ||
        !bills.length
    ) {
        table.innerHTML = `
            <tr>
                <td
                    colspan="6"
                    class="loading"
                >
                    No bills found.
                </td>
            </tr>
        `;

        return;
    }

    table.innerHTML =
        bills.map(bill => {

            const encodedName =
                encodeURIComponent(bill.name);

            return `
                <tr>

                    <td>

                        <button
                            class="bill-name bill-name-button"
                            type="button"
                            onclick="openBillDetails('${encodedName}')"
                            title="View LifeOps explainability"
                        >
                            ${escapeHtml(bill.name)}
                        </button>

                    </td>


                    <td>

                        <span class="amount">
                            ${formatMoney(
                                bill.amount,
                                bill.currency
                            )}
                        </span>

                    </td>


                    <td>

                        <span class="due-date">
                            ${escapeHtml(
                                bill.due_date
                            )}
                        </span>

                    </td>


                    <td>
                        ${getDecisionBadge(bill)}
                    </td>


                    <td>
                        ${getStatusBadge(bill)}
                    </td>


                    <td>
                        ${getActions(bill)}
                    </td>

                </tr>
            `;

        }).join("");
}


/* ============================================================
   SUMMARY
   ============================================================ */

function updateSummary(summary = {}) {
    document
        .getElementById("totalBills")
        .textContent =
            summary.total_bills ?? 0;


    document
        .getElementById("totalPaid")
        .textContent =
            formatMoney(
                summary.total_paid || 0
            );


    const paidCount =
        summary.paid_count ?? 0;

    document
        .getElementById("paidCount")
        .textContent =
            `${paidCount} paid bill${
                paidCount === 1
                    ? ""
                    : "s"
            }`;


    document
        .getElementById("approvalAmount")
        .textContent =
            formatMoney(
                summary.awaiting_approval || 0
            );


    const approvalCount =
        summary.approval_count ?? 0;

    document
        .getElementById("approvalCount")
        .textContent =
            `${approvalCount} bill${
                approvalCount === 1
                    ? ""
                    : "s"
            } require attention`;


    document
        .getElementById("blockedAmount")
        .textContent =
            formatMoney(
                summary.blocked_amount || 0
            );


    const blockedCount =
        summary.blocked_count ?? 0;

    document
        .getElementById("blockedCount")
        .textContent =
            `${blockedCount} blocked bill${
                blockedCount === 1
                    ? ""
                    : "s"
            }`;
}


/* ============================================================
   LOAD DASHBOARD
   ============================================================ */

async function loadDashboard() {
    try {
        const response =
            await fetch(
                `${API}/dashboard`
            );

        if (!response.ok) {
            throw new Error(
                "Failed to load dashboard"
            );
        }

        const data =
            await response.json();

        updateSummary(
            data.summary || {}
        );

        renderBills(
            data.bills || []
        );

    } catch (error) {
        console.error(
            "Dashboard error:",
            error
        );

        showToast(
            "Unable to connect to LifeOps API"
        );
    }
}


/* ============================================================
   BILL DETAIL STATUS BADGE
   ============================================================ */

function getDetailStatusBadge(status) {
    const normalized =
        String(
            status || "PENDING"
        ).toUpperCase();

    if (
        normalized === "PAID" ||
        normalized === "COMPLETED" ||
        normalized === "APPROVED" ||
        normalized === "AUTO_HANDLE"
    ) {
        return `
            <span class="badge badge-paid">
                ${escapeHtml(
                    normalized.replaceAll(
                        "_",
                        " "
                    )
                )}
            </span>
        `;
    }

    if (
        normalized === "NEEDS_APPROVAL"
    ) {
        return `
            <span class="badge badge-approval">
                NEEDS APPROVAL
            </span>
        `;
    }

    if (
        normalized === "BLOCK" ||
        normalized === "BLOCKED" ||
        normalized === "FAILED"
    ) {
        return `
            <span class="badge badge-blocked">
                ${escapeHtml(normalized)}
            </span>
        `;
    }

    return `
        <span class="badge badge-pending">
            ${escapeHtml(
                normalized.replaceAll(
                    "_",
                    " "
                )
            )}
        </span>
    `;
}


/* ============================================================
   CLOSE BILL DETAIL DRAWER
   ============================================================ */

function closeBillDetails() {
    const overlay =
        document.getElementById(
            "billDetailOverlay"
        );

    if (!overlay) {
        return;
    }

    overlay.classList.remove("show");

    document.body.classList.remove(
        "bill-detail-open"
    );
}


/* ============================================================
   RENDER BILL DETAILS
   ============================================================ */

function renderBillDetails(data) {
    const bill =
        data.bill || {};

    const safety =
        data.safety || {};

    const originalDecision =
        data.original_decision || null;

    const latestDecision =
        data.latest_decision || null;

    const approval =
        data.human_approval || {};

    const payment =
        data.payment || null;

    const history =
        Array.isArray(data.history)
            ? data.history
            : [];


    /*
     * Header
     */

    document
        .getElementById("detailBillName")
        .textContent =
            bill.name ||
            "Bill Details";


    document
        .getElementById(
            "detailBillCategory"
        )
        .textContent =
            `${
                bill.category ||
                "Financial obligation"
            } • Due ${
                formatDetailDate(
                    bill.due_date
                )
            }`;


    /*
     * Explainability reason
     */

    const flagReason =
        originalDecision?.reason ||
        latestDecision?.reason ||
        "LifeOps has not recorded a safety explanation for this bill yet.";


    /*
     * Difference percentage
     */

    const difference =
        safety.difference_percentage;

    let differenceText = "—";

    if (
        difference !== null &&
        difference !== undefined
    ) {
        const number =
            Number(difference);

        differenceText =
            `${
                number >= 0
                    ? "+"
                    : ""
            }${number.toFixed(2)}%`;
    }


    /*
     * History
     */

    let historyHtml = `
        <div class="bill-detail-empty-note">
            No historical payments recorded.
        </div>
    `;

    if (history.length) {
        historyHtml =
            history.map(item => `
                <div class="bill-history-row">

                    <span class="bill-history-date">
                        ${escapeHtml(
                            formatDetailDate(
                                item.paid_date
                            )
                        )}
                    </span>

                    <strong class="bill-history-amount">
                        ${escapeHtml(
                            formatMoney(
                                item.amount,
                                item.currency ||
                                bill.currency ||
                                "NGN"
                            )
                        )}
                    </strong>

                </div>
            `).join("");
    }


    const content =
        document.getElementById(
            "billDetailContent"
        );


    content.innerHTML = `

        <!-- CURRENT BILL -->

        <section class="bill-detail-section">

            <p class="bill-detail-section-title">
                Current Bill
            </p>


            <div class="bill-detail-summary">

                <div>

                    <div class="bill-detail-amount">

                        ${escapeHtml(
                            formatMoney(
                                bill.amount,
                                bill.currency || "NGN"
                            )
                        )}

                    </div>


                    <div class="bill-detail-summary-meta">

                        Due
                        ${escapeHtml(
                            formatDetailDate(
                                bill.due_date
                            )
                        )}

                    </div>

                </div>


                ${getDetailStatusBadge(
                    bill.status
                )}

            </div>

        </section>


        <!-- AGENT DECISION -->

        <section class="bill-detail-section">

            <p class="bill-detail-section-title">
                Agent Decision
            </p>


            <div class="bill-detail-row">

                <span>
                    Original safety decision
                </span>

                <strong>

                    ${
                        originalDecision
                            ? getDetailStatusBadge(
                                originalDecision.decision
                            )
                            : "—"
                    }

                </strong>

            </div>


            <div class="bill-detail-row">

                <span>
                    Latest decision
                </span>

                <strong>

                    ${
                        latestDecision
                            ? getDetailStatusBadge(
                                latestDecision.decision
                            )
                            : "—"
                    }

                </strong>

            </div>


            <div class="bill-detail-reason">

                <strong>
                    WHY LIFEOPS MADE THIS DECISION
                </strong>

                <p>
                    ${escapeHtml(flagReason)}
                </p>

            </div>

        </section>


        <!-- SAFETY CHECK -->

        <section class="bill-detail-section">

            <p class="bill-detail-section-title">
                Safety Check
            </p>


            <div class="bill-detail-metrics">


                <div class="bill-detail-metric">

                    <span>
                        Automatic Limit
                    </span>

                    <strong>

                        ${escapeHtml(
                            formatMoney(
                                safety.automatic_payment_limit,
                                bill.currency || "NGN"
                            )
                        )}

                    </strong>

                </div>


                <div class="bill-detail-metric">

                    <span>
                        Historical Average
                    </span>

                    <strong>

                        ${
                            safety.historical_average ===
                                null ||
                            safety.historical_average ===
                                undefined

                                ? "—"

                                : escapeHtml(
                                    formatMoney(
                                        safety.historical_average,
                                        bill.currency ||
                                        "NGN"
                                    )
                                )
                        }

                    </strong>

                </div>


                <div class="bill-detail-metric">

                    <span>
                        Difference
                    </span>

                    <strong>
                        ${escapeHtml(
                            differenceText
                        )}
                    </strong>

                </div>


            </div>


            <div class="bill-detail-row bill-detail-limit-row">

                <span>
                    Exceeds automatic limit
                </span>

                <strong>
                    ${
                        safety.exceeds_auto_payment_limit
                            ? "Yes"
                            : "No"
                    }
                </strong>

            </div>

        </section>


        <!-- HISTORICAL SPENDING -->

        <section class="bill-detail-section">

            <p class="bill-detail-section-title">
                Historical Spending
            </p>

            <div class="bill-history-list">
                ${historyHtml}
            </div>

        </section>


        <!-- HUMAN APPROVAL -->

        <section class="bill-detail-section">

            <p class="bill-detail-section-title">
                Human Approval
            </p>


            <div class="bill-detail-row">

                <span>
                    Approval status
                </span>

                <strong>

                    ${
                        approval.approved
                            ? "Approved by human"
                            : "Not required / not approved"
                    }

                </strong>

            </div>


            <div class="bill-detail-row">

                <span>
                    Approval time
                </span>

                <strong>

                    ${
                        approval.created_at
                            ? escapeHtml(
                                formatDetailDate(
                                    approval.created_at
                                )
                            )
                            : "—"
                    }

                </strong>

            </div>

        </section>


        <!-- PAYMENT -->

        <section class="bill-detail-section">

            <p class="bill-detail-section-title">
                Payment
            </p>


            <div class="bill-detail-row">

                <span>
                    Status
                </span>

                <strong>

                    ${
                        payment
                            ? getDetailStatusBadge(
                                payment.status
                            )
                            : "Not paid"
                    }

                </strong>

            </div>


            <div class="bill-detail-row">

                <span>
                    Amount
                </span>

                <strong>

                    ${
                        payment
                            ? escapeHtml(
                                formatMoney(
                                    payment.amount,
                                    payment.currency ||
                                    bill.currency ||
                                    "NGN"
                                )
                            )
                            : "—"
                    }

                </strong>

            </div>


            <div class="bill-detail-row">

                <span>
                    Reference
                </span>

                <strong class="bill-detail-reference">

                    ${
                        payment?.reference
                            ? escapeHtml(
                                payment.reference
                            )
                            : "—"
                    }

                </strong>

            </div>

        </section>

    `;
}


/* ============================================================
   OPEN BILL DETAIL DRAWER
   ============================================================ */

async function openBillDetails(encodedName) {
    const overlay =
        document.getElementById(
            "billDetailOverlay"
        );

    const content =
        document.getElementById(
            "billDetailContent"
        );

    if (
        !overlay ||
        !content
    ) {
        console.error(
            "Bill detail drawer elements were not found."
        );

        return;
    }


    const billName =
        decodeURIComponent(
            encodedName
        );


    /*
     * Set loading state.
     */

    document
        .getElementById(
            "detailBillName"
        )
        .textContent =
            billName;


    document
        .getElementById(
            "detailBillCategory"
        )
        .textContent =
            "Retrieving explainability data...";


    content.innerHTML = `
        <div class="bill-detail-loading">

            <span class="activity-spinner"></span>

            <div>

                <strong>
                    Loading bill details
                </strong>

                <p>
                    Retrieving LifeOps decision history...
                </p>

            </div>

        </div>
    `;


    /*
     * Open drawer immediately.
     */

    overlay.classList.add("show");

    document.body.classList.add(
        "bill-detail-open"
    );


    /*
     * Load explainability endpoint.
     */

    try {
        const response =
            await fetch(
                `${API}/bill/${encodedName}/details`
            );


        if (!response.ok) {
            throw new Error(
                `Unable to load details for ${billName}.`
            );
        }


        const data =
            await response.json();


        if (data.error) {
            throw new Error(
                data.error
            );
        }


        renderBillDetails(data);

    } catch (error) {
        console.error(
            "Bill details error:",
            error
        );


        content.innerHTML = `
            <div class="bill-detail-error">

                <strong>
                    Unable to load bill details
                </strong>

                <p>
                    ${escapeHtml(
                        error.message
                    )}
                </p>

            </div>
        `;
    }
}


/* ============================================================
   APPROVAL MODAL
   ============================================================ */

function openApprovalModal(
    encodedName,
    amount,
    encodedReason
) {
    const billName =
        decodeURIComponent(
            encodedName
        );

    const reason =
        decodeURIComponent(
            encodedReason
        );


    pendingApproval = {
        encodedName,
        billName,
        amount,
        reason
    };


    /*
     * Reset buttons every time the modal opens.
     */

    const confirmButton =
        document.getElementById(
            "confirmApprovalButton"
        );

    const cancelButton =
        document.getElementById(
            "cancelApprovalButton"
        );


    confirmButton.disabled = false;

    cancelButton.disabled = false;

    confirmButton.textContent =
        "Approve & Pay";


    document
        .getElementById(
            "modalBillName"
        )
        .textContent =
            billName;


    document
        .getElementById(
            "modalBillAmount"
        )
        .textContent =
            formatMoney(amount);


    document
        .getElementById(
            "modalReason"
        )
        .textContent =
            reason;


    document
        .getElementById(
            "modalError"
        )
        .textContent = "";


    document
        .getElementById(
            "approvalModal"
        )
        .classList.add("show");
}


function closeApprovalModal() {
    const modal =
        document.getElementById(
            "approvalModal"
        );

    modal.classList.remove("show");

    pendingApproval = null;
}


/* ============================================================
   APPROVE AND PAY
   ============================================================ */

async function approveAndPay() {
    if (!pendingApproval) {
        return;
    }


    const button =
        document.getElementById(
            "confirmApprovalButton"
        );


    const cancelButton =
        document.getElementById(
            "cancelApprovalButton"
        );


    const errorBox =
        document.getElementById(
            "modalError"
        );


    const approval =
        pendingApproval;


    button.disabled = true;

    cancelButton.disabled = true;

    button.textContent =
        "Authorizing...";

    errorBox.textContent = "";


    try {

        /*
         * STEP 1
         * Human approval
         */

        const approvalResponse =
            await fetch(
                `${API}/bill/${approval.encodedName}/approve`,
                {
                    method: "POST"
                }
            );


        if (!approvalResponse.ok) {
            throw new Error(
                "LifeOps could not approve this payment."
            );
        }


        const approvalData =
            await approvalResponse.json();


        /*
         * STEP 2
         * Execute payment
         */

        button.textContent =
            "Processing payment...";


        const paymentResponse =
            await fetch(
                `${API}/bill/${approval.encodedName}/pay`,
                {
                    method: "POST"
                }
            );


        if (!paymentResponse.ok) {
            throw new Error(
                "Approval succeeded, but payment could not be completed."
            );
        }


        const paymentData =
            await paymentResponse.json();


        /*
         * STEP 3
         * Close modal
         */

        closeApprovalModal();


        showToast(
            `${approval.billName} approved and paid successfully`
        );


        /*
         * STEP 4
         * Refresh dashboard + activity.
         */

        await loadDashboard();

        await loadActivityHistory();


        console.log(
            approvalData,
            paymentData
        );

    } catch (error) {
        console.error(
            "Approval/payment error:",
            error
        );


        errorBox.textContent =
            error.message;


        button.disabled = false;

        cancelButton.disabled = false;

        button.textContent =
            "Approve & Pay";
    }
}


/* ============================================================
   DIRECT PAYMENT
   ============================================================ */

async function payBill(encodedName) {
    const billName =
        decodeURIComponent(
            encodedName
        );


    const confirmed =
        confirm(
            `Execute payment for ${billName}?`
        );


    if (!confirmed) {
        return;
    }


    try {
        const response =
            await fetch(
                `${API}/bill/${encodedName}/pay`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {
            throw new Error(
                "Payment request failed"
            );
        }


        const data =
            await response.json();


        showToast(
            data.result ||
            `${billName} payment completed`
        );


        await loadDashboard();

        await loadActivityHistory();

    } catch (error) {
        console.error(
            "Payment error:",
            error
        );


        showToast(
            "Payment request failed"
        );
    }
}


/* ============================================================
   PERSISTED ACTIVITY
   ============================================================ */

function renderPersistedActivity(events) {
    const container =
        document.getElementById(
            "activityOutput"
        );


    if (
        !Array.isArray(events) ||
        !events.length
    ) {
        container.innerHTML = `
            <div class="activity-empty">

                <div class="activity-empty-icon">
                    ◎
                </div>

                <strong>
                    No activity yet
                </strong>

                <p>
                    Run LifeOps to begin a financial operations cycle.
                </p>

            </div>
        `;

        return;
    }


    const normalizedEvents =
        events.map(event => {

            let type = "info";

            let icon = "•";

            let label =
                "LIFEOPS EVENT";

            let title =
                event.bill_name ||
                "LifeOps event";


            /*
             * PAYMENT
             */

            if (
                event.type === "payment" &&
                event.status === "COMPLETED"
            ) {
                type = "success";

                icon = "✓";

                label = "PAYMENT";

                title =
                    `${event.bill_name} paid`;
            }


            /*
             * HUMAN REVIEW
             */

            else if (
                event.status ===
                "NEEDS_APPROVAL"
            ) {
                type = "warning";

                icon = "!";

                label =
                    "HUMAN REVIEW";

                title =
                    `${event.bill_name} requires approval`;
            }


            /*
             * APPROVED
             */

            else if (
                event.status === "APPROVED"
            ) {
                type = "success";

                icon = "✓";

                label =
                    "HUMAN APPROVAL";

                title =
                    `${event.bill_name} approved`;
            }


            /*
             * AUTO HANDLE
             */

            else if (
                event.status === "AUTO_HANDLE"
            ) {
                type =
                    "investigation";

                icon = "⌕";

                label =
                    "AUTO DECISION";

                title =
                    `${event.bill_name} cleared automatically`;
            }


            /*
             * BLOCK
             */

            else if (
                event.status === "BLOCK" ||
                event.status === "BLOCKED"
            ) {
                type = "danger";

                icon = "×";

                label =
                    "SAFETY BLOCK";

                title =
                    `${event.bill_name} blocked`;
            }


            const amount =
                event.amount !== null &&
                event.amount !== undefined

                    ? formatMoney(
                        Number(
                            event.amount
                        ),
                        event.currency ||
                        "NGN"
                    )

                    : "";


            return {
                type,
                icon,
                label,
                title,
                amount,

                time:
                    formatActivityTime(
                        event.created_at
                    ),

                message:
                    event.message ||
                    "LifeOps event recorded.",

                reference:
                    event.reference || ""
            };
        });


    container.innerHTML = `

        <div class="activity-timeline">

            ${normalizedEvents.map(
                (event, index) => `

                    <div class="activity-event">


                        <div class="activity-timeline-column">


                            <div class="activity-icon ${event.type}">
                                ${escapeHtml(
                                    event.icon
                                )}
                            </div>


                            ${
                                index <
                                normalizedEvents.length - 1

                                    ? `
                                        <div
                                            class="activity-line"
                                        ></div>
                                    `

                                    : ""
                            }


                        </div>


                        <div class="activity-card">


                            <div class="activity-card-top">


                                <div class="activity-card-heading">


                                    <span
                                        class="activity-label ${event.type}"
                                    >
                                        ${escapeHtml(
                                            event.label
                                        )}
                                    </span>


                                    <h4>
                                        ${escapeHtml(
                                            event.title
                                        )}
                                    </h4>


                                </div>


                                <div class="activity-card-meta">


                                    ${
                                        event.amount

                                            ? `
                                                <strong
                                                    class="activity-amount"
                                                >
                                                    ${escapeHtml(
                                                        event.amount
                                                    )}
                                                </strong>
                                            `

                                            : ""
                                    }


                                    <span class="activity-time">

                                        ${escapeHtml(
                                            event.time
                                        )}

                                    </span>


                                </div>


                            </div>


                            <p class="activity-message">
                                ${escapeHtml(
                                    event.message
                                )}
                            </p>


                            ${
                                event.reference

                                    ? `
                                        <div
                                            class="activity-reference"
                                            style="
                                                margin-top: 8px;
                                                font-size: 10px;
                                                color: #94a3b8;
                                            "
                                        >
                                            Transaction:
                                            ${escapeHtml(
                                                event.reference
                                            )}
                                        </div>
                                    `

                                    : ""
                            }


                        </div>


                    </div>

                `
            ).join("")}

        </div>
    `;
}


/* ============================================================
   LOAD ACTIVITY
   ============================================================ */

async function loadActivityHistory() {
    try {
        const response =
            await fetch(
                `${API}/activity`
            );


        if (!response.ok) {
            throw new Error(
                "Failed to load activity history"
            );
        }


        const data =
            await response.json();


        renderPersistedActivity(
            data.activity || []
        );

    } catch (error) {
        console.error(
            "Activity history error:",
            error
        );


        document
            .getElementById(
                "activityOutput"
            )
            .innerHTML = `

                <div class="activity-empty">

                    <div class="activity-empty-icon">
                        !
                    </div>

                    <strong>
                        Unable to load activity
                    </strong>

                    <p>
                        LifeOps could not retrieve persisted activity history.
                    </p>

                </div>
            `;
    }
}


/* ============================================================
   RUN LIFEOPS
   ============================================================ */

async function runLifeOps() {
    const button =
        document.getElementById(
            "runButton"
        );


    button.disabled = true;


    button.innerHTML = `
        <span>⟳</span>
        Running...
    `;


    document
        .getElementById(
            "activityOutput"
        )
        .innerHTML = `

            <div class="activity-running">

                <span
                    class="activity-spinner"
                ></span>

                <div>

                    <strong>
                        LifeOps is running
                    </strong>

                    <p>
                        Investigating bills and evaluating payment safety...
                    </p>

                </div>

            </div>
        `;


    try {
        const response =
            await fetch(
                `${API}/run`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {
            throw new Error(
                "LifeOps workflow failed"
            );
        }


        await response.json();


        await loadDashboard();

        await loadActivityHistory();


        showToast(
            "LifeOps workflow completed"
        );

    } catch (error) {
        console.error(
            "LifeOps workflow error:",
            error
        );


        document
            .getElementById(
                "activityOutput"
            )
            .innerHTML = `

                <div class="activity-error">

                    <strong>
                        LifeOps failed
                    </strong>

                    <p>
                        ${escapeHtml(
                            error.message
                        )}
                    </p>

                </div>
            `;


        showToast(
            "LifeOps workflow failed"
        );

    } finally {
        button.disabled = false;


        button.innerHTML = `
            <span>▶</span>
            Run LifeOps
        `;
    }
}


/* ============================================================
   EVENT LISTENERS
   ============================================================ */

function initializeEventListeners() {

    /*
     * Run LifeOps
     */

    const runButton =
        document.getElementById(
            "runButton"
        );

    if (runButton) {
        runButton.addEventListener(
            "click",
            runLifeOps
        );
    }


    /*
     * Approval
     */

    const confirmApprovalButton =
        document.getElementById(
            "confirmApprovalButton"
        );

    if (confirmApprovalButton) {
        confirmApprovalButton
            .addEventListener(
                "click",
                approveAndPay
            );
    }


    const cancelApprovalButton =
        document.getElementById(
            "cancelApprovalButton"
        );

    if (cancelApprovalButton) {
        cancelApprovalButton
            .addEventListener(
                "click",
                closeApprovalModal
            );
    }


    const approvalModal =
        document.getElementById(
            "approvalModal"
        );

    if (approvalModal) {
        approvalModal.addEventListener(
            "click",
            event => {

                if (
                    event.target ===
                    approvalModal
                ) {
                    closeApprovalModal();
                }

            }
        );
    }


    /*
     * Bill detail drawer
     */

    const closeDetailButton =
        document.getElementById(
            "closeBillDetailButton"
        );

    if (closeDetailButton) {
        closeDetailButton.addEventListener(
            "click",
            closeBillDetails
        );
    }


    const detailOverlay =
        document.getElementById(
            "billDetailOverlay"
        );

    if (detailOverlay) {
        detailOverlay.addEventListener(
            "click",
            event => {

                /*
                 * Only close when the dark
                 * background itself is clicked.
                 */

                if (
                    event.target ===
                    detailOverlay
                ) {
                    closeBillDetails();
                }

            }
        );
    }


    /*
     * Escape key
     */

    document.addEventListener(
        "keydown",
        event => {

            if (
                event.key !== "Escape"
            ) {
                return;
            }


            if (
                approvalModal &&
                approvalModal.classList.contains(
                    "show"
                )
            ) {
                closeApprovalModal();
            }


            if (
                detailOverlay &&
                detailOverlay.classList.contains(
                    "show"
                )
            ) {
                closeBillDetails();
            }

        }
    );
}


/* ============================================================
   STARTUP
   ============================================================ */

initializeEventListeners();

loadDashboard();

loadActivityHistory();


/* ============================================================
   AUTOMATIC REFRESH
   ============================================================ */

setInterval(
    async () => {

        await loadDashboard();

        await loadActivityHistory();

    },
    15000
);
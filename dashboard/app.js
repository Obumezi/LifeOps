const API = "/api";



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
    ).format(amount || 0);

}



function showToast(message) {

    const toast =
        document.getElementById("toast");


    toast.textContent =
        message || "LifeOps action completed";


    toast.classList.add("show");


    setTimeout(() => {

        toast.classList.remove("show");

    }, 3000);

}



function escapeHtml(value) {

    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}



function getCurrentTime() {

    return new Intl.DateTimeFormat(
        "en-NG",
        {
            hour: "2-digit",
            minute: "2-digit"
        }
    ).format(new Date());

}



/* ============================================================
   ACTIVITY FEED
   ============================================================ */


function renderActivity(result) {

    const container =
        document.getElementById("activityOutput");


    if (!result) {

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


    const text = String(result);

    const events = [];



    /* --------------------------------------------------------
       INVESTIGATION
       -------------------------------------------------------- */


    if (
        text.includes(
            "LifeOps completed a deterministic investigation"
        )
    ) {

        events.push({

            type: "investigation",

            icon: "⌕",

            label: "ANALYSIS",

            title:
                "Investigation complete",

            message:
                "LifeOps analysed all pending financial obligations and evaluated them against payment safety policies."

        });

    }



    /* --------------------------------------------------------
       APPROVAL REQUIRED
       -------------------------------------------------------- */


    const approvalMatch = text.match(
        /([^|\n]+)\s*\|\s*NGN\s*([\d,]+)\s*\|\s*Decision:\s*NEEDS_APPROVAL\s*\|\s*Reason:\s*([^\n]+)/
    );


    if (approvalMatch) {

        const billName =
            approvalMatch[1].trim();

        const amount =
            approvalMatch[2].trim();

        const reason =
            approvalMatch[3].trim();


        events.push({

            type: "warning",

            icon: "!",

            label: "HUMAN REVIEW",

            title:
                `${billName} requires approval`,

            amount:
                `NGN ${amount}`,

            message:
                reason

        });

    }



    /* --------------------------------------------------------
       PAID BILLS
       -------------------------------------------------------- */


    const paidRegex =
        /✓\s*([^—\n]+)\s*—\s*NGN\s*([\d,]+)/g;


    const paidMatches =
        [...text.matchAll(paidRegex)];


    const seenPayments =
        new Set();


    paidMatches.forEach(match => {

        const name =
            match[1].trim();

        const amount =
            match[2].trim();


        const key =
            `${name}-${amount}`;


        if (seenPayments.has(key)) {
            return;
        }


        seenPayments.add(key);


        events.push({

            type: "success",

            icon: "✓",

            label: "AUTO PAYMENT",

            title:
                `${name} paid`,

            amount:
                `NGN ${amount}`,

            message:
                "Payment completed automatically after passing LifeOps safety checks."

        });

    });



    /* --------------------------------------------------------
       BLOCKED ITEMS
       -------------------------------------------------------- */


    const blockedRegex =
        /BLOCK(?:ED)?:\s*([^\n]+)/g;


    const blockedMatches =
        [...text.matchAll(blockedRegex)];


    blockedMatches.forEach(match => {

        const message =
            match[1].trim();


        if (
            message.toLowerCase() === "none" ||
            message.toLowerCase().includes("ngn 0")
        ) {
            return;
        }


        events.push({

            type: "danger",

            icon: "×",

            label: "SAFETY BLOCK",

            title:
                "Payment blocked",

            message:
                message

        });

    });



    /* --------------------------------------------------------
       FALLBACK
       -------------------------------------------------------- */


    if (!events.length) {

        events.push({

            type: "info",

            icon: "✓",

            label: "COMPLETE",

            title:
                "LifeOps cycle complete",

            message:
                "No new financial obligations required action."

        });

    }



    const time =
        getCurrentTime();



    container.innerHTML = `

        <div class="activity-timeline">

            ${events.map((event, index) => `

                <div class="activity-event">


                    <div class="activity-timeline-column">


                        <div class="activity-icon ${event.type}">

                            ${escapeHtml(event.icon)}

                        </div>


                        ${
                            index < events.length - 1
                                ? `<div class="activity-line"></div>`
                                : ""
                        }


                    </div>



                    <div class="activity-card">


                        <div class="activity-card-top">


                            <div class="activity-card-heading">


                                <span class="activity-label ${event.type}">

                                    ${escapeHtml(event.label)}

                                </span>


                                <h4>

                                    ${escapeHtml(event.title)}

                                </h4>


                            </div>



                            <div class="activity-card-meta">


                                ${
                                    event.amount
                                        ? `

                                            <strong class="activity-amount">

                                                ${escapeHtml(event.amount)}

                                            </strong>

                                        `
                                        : ""
                                }


                                <span class="activity-time">

                                    ${escapeHtml(time)}

                                </span>


                            </div>


                        </div>



                        <p class="activity-message">

                            ${escapeHtml(event.message)}

                        </p>


                    </div>


                </div>

            `).join("")}


        </div>

    `;

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
        bill.decision === "BLOCK"
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

    if (!bill.decision) {

        return `

            <span class="badge badge-pending">

                NO DECISION

            </span>

        `;

    }


    if (
        bill.decision === "AUTO_HANDLE"
    ) {

        return `

            <span class="badge badge-paid">

                AUTO HANDLE

            </span>

        `;

    }


    if (
        bill.decision === "APPROVED"
    ) {

        return `

            <span class="badge badge-paid">

                APPROVED

            </span>

        `;

    }


    if (
        bill.decision === "NEEDS_APPROVAL"
    ) {

        return `

            <span class="badge badge-approval">

                NEEDS APPROVAL

            </span>

        `;

    }


    if (
        bill.decision === "BLOCK"
    ) {

        return `

            <span class="badge badge-blocked">

                BLOCKED

            </span>

        `;

    }


    return `

        <span class="badge badge-pending">

            ${escapeHtml(bill.decision)}

        </span>

    `;

}



/* ============================================================
   BILL ACTIONS
   ============================================================ */


function getActions(bill) {

    const encodedName =
        encodeURIComponent(bill.name);


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



    if (
        bill.decision === "NEEDS_APPROVAL"
    ) {

        return `

            <div class="action-group">

                <button
                    class="action-button approve"
                    onclick="approveBill('${encodedName}')"
                >

                    Approve

                </button>

                <button
                    class="action-button pay"
                    disabled
                >

                    Pay

                </button>

            </div>

        `;

    }



    if (
        bill.decision === "AUTO_HANDLE" ||
        bill.decision === "APPROVED"
    ) {

        return `

            <div class="action-group">

                <button
                    class="action-button pay"
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


    if (!Array.isArray(bills) || !bills.length) {

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
        bills.map(bill => `


            <tr>


                <td>

                    <div class="bill-name">

                        ${escapeHtml(bill.name)}

                    </div>

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

                        ${escapeHtml(bill.due_date)}

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


        `).join("");

}



/* ============================================================
   SUMMARY
   ============================================================ */


function updateSummary(summary) {

    document
        .getElementById("totalBills")
        .textContent =
            summary.total_bills ?? 0;


    document
        .getElementById("totalPaid")
        .textContent =
            formatMoney(
                summary.total_paid
            );


    document
        .getElementById("paidCount")
        .textContent =
            `${summary.paid_count ?? 0} paid bill${
                summary.paid_count === 1
                    ? ""
                    : "s"
            }`;


    document
        .getElementById("approvalAmount")
        .textContent =
            formatMoney(
                summary.awaiting_approval
            );


    document
        .getElementById("approvalCount")
        .textContent =
            `${summary.approval_count ?? 0} bill${
                summary.approval_count === 1
                    ? ""
                    : "s"
            } require attention`;


    document
        .getElementById("blockedAmount")
        .textContent =
            formatMoney(
                summary.blocked_amount
            );


    document
        .getElementById("blockedCount")
        .textContent =
            `${summary.blocked_count ?? 0} blocked bill${
                summary.blocked_count === 1
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
            data.summary
        );


        renderBills(
            data.bills
        );


    } catch (error) {

        console.error(error);


        showToast(
            "Unable to connect to LifeOps API"
        );

    }

}



/* ============================================================
   APPROVE BILL
   ============================================================ */


async function approveBill(encodedName) {

    const billName =
        decodeURIComponent(
            encodedName
        );


    const confirmed =
        confirm(
            `Approve payment for ${billName}?`
        );


    if (!confirmed) {
        return;
    }


    try {

        const response =
            await fetch(
                `/api/bill/${encodedName}/approve`,
                {
                    method: "POST"
                }
            );


        if (!response.ok) {

            throw new Error(
                "Approval request failed"
            );

        }


        const data =
            await response.json();


        renderActivity(
            `APPROVED: ${billName}\n${data.result}`
        );


        showToast(
            data.result ||
            `${billName} approved`
        );


        await loadDashboard();


    } catch (error) {

        console.error(error);


        showToast(
            "Approval request failed"
        );

    }

}



/* ============================================================
   PAY BILL
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
                `/api/bill/${encodedName}/pay`,
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


        renderActivity(
            `✓ ${billName} — payment completed\n${data.result}`
        );


        showToast(
            data.result ||
            `${billName} payment completed`
        );


        await loadDashboard();


    } catch (error) {

        console.error(error);


        showToast(
            "Payment request failed"
        );

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
        .getElementById("activityOutput")
        .innerHTML = `


            <div class="activity-running">


                <span class="activity-spinner"></span>


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


        const data =
            await response.json();


        renderActivity(
            data.result ||
            "LifeOps workflow completed."
        );


        showToast(
            "LifeOps workflow completed"
        );


        await loadDashboard();


    } catch (error) {

        console.error(error);


        document
            .getElementById("activityOutput")
            .innerHTML = `


                <div class="activity-error">

                    <strong>
                        LifeOps failed
                    </strong>

                    <p>
                        ${escapeHtml(error.message)}
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
   STARTUP
   ============================================================ */


document
    .getElementById("runButton")
    .addEventListener(
        "click",
        runLifeOps
    );


loadDashboard();



/* Refresh dashboard every 15 seconds */

setInterval(
    loadDashboard,
    15000
);
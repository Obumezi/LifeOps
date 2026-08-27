const API = "/api";


function formatMoney(amount, currency = "NGN") {

    return new Intl.NumberFormat("en-NG", {
        style: "currency",
        currency: currency,
        maximumFractionDigits: 0
    }).format(amount);

}


function showToast(message) {

    const toast = document.getElementById("toast");

    toast.textContent = message;

    toast.classList.add("show");

    setTimeout(() => {
        toast.classList.remove("show");
    }, 3000);

}


function getStatusBadge(bill) {

    if (
        bill.status === "paid" &&
        bill.payment_status === "COMPLETED"
    ) {
        return `<span class="badge badge-paid">PAID</span>`;
    }

    if (bill.decision === "NEEDS_APPROVAL") {
        return `<span class="badge badge-approval">AWAITING APPROVAL</span>`;
    }

    if (bill.decision === "BLOCK") {
        return `<span class="badge badge-blocked">BLOCKED</span>`;
    }

    return `<span class="badge badge-pending">PENDING</span>`;
}


function getDecisionBadge(bill) {

    if (!bill.decision) {
        return `<span class="badge badge-pending">NO DECISION</span>`;
    }

    if (bill.decision === "AUTO_HANDLE") {
        return `<span class="badge badge-paid">AUTO HANDLE</span>`;
    }

    if (bill.decision === "APPROVED") {
        return `<span class="badge badge-paid">APPROVED</span>`;
    }

    if (bill.decision === "NEEDS_APPROVAL") {
        return `<span class="badge badge-approval">NEEDS APPROVAL</span>`;
    }

    if (bill.decision === "BLOCK") {
        return `<span class="badge badge-blocked">BLOCKED</span>`;
    }

    return `<span class="badge badge-pending">${bill.decision}</span>`;
}


function getActions(bill) {

    if (
        bill.status === "paid" &&
        bill.payment_status === "COMPLETED"
    ) {
        return `<span class="badge badge-paid">Completed</span>`;
    }

    if (bill.decision === "NEEDS_APPROVAL") {

        return `
            <div class="action-group">

                <button
                    class="action-button approve"
                    onclick="approveBill('${encodeURIComponent(bill.name)}')"
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
                    onclick="payBill('${encodeURIComponent(bill.name)}')"
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


function renderBills(bills) {

    const table = document.getElementById("billsTable");

    if (!bills.length) {

        table.innerHTML = `
            <tr>
                <td colspan="6" class="loading">
                    No bills found.
                </td>
            </tr>
        `;

        return;
    }


    table.innerHTML = bills.map(bill => {

        return `
            <tr>

                <td>
                    <div class="bill-name">
                        ${bill.name}
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
                        ${bill.due_date}
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


function updateSummary(summary) {

    document.getElementById("totalBills").textContent =
        summary.total_bills;

    document.getElementById("totalPaid").textContent =
        formatMoney(summary.total_paid);

    document.getElementById("paidCount").textContent =
        `${summary.paid_count} paid bill${summary.paid_count === 1 ? "" : "s"}`;

    document.getElementById("approvalAmount").textContent =
        formatMoney(summary.awaiting_approval);

    document.getElementById("approvalCount").textContent =
        `${summary.approval_count} bill${summary.approval_count === 1 ? "" : "s"} require attention`;

    document.getElementById("blockedAmount").textContent =
        formatMoney(summary.blocked_amount);

    document.getElementById("blockedCount").textContent =
        `${summary.blocked_count} blocked bill${summary.blocked_count === 1 ? "" : "s"}`;
}


async function loadDashboard() {

    try {

        const response = await fetch(
            `${API}/dashboard`
        );

        if (!response.ok) {
            throw new Error("Failed to load dashboard");
        }

        const data = await response.json();

        updateSummary(data.summary);

        renderBills(data.bills);

    } catch (error) {

        console.error(error);

        showToast("Unable to connect to LifeOps API");

    }

}


async function approveBill(encodedName) {

    const billName = decodeURIComponent(encodedName);

    const confirmed = confirm(
        `Approve payment for ${billName}?`
    );

    if (!confirmed) {
        return;
    }


    try {

        const response = await fetch(
            `/api/bill/${encodedName}/approve`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        document.getElementById("activityOutput").textContent =
            data.result;

        showToast(data.result);

        await loadDashboard();

    } catch (error) {

        console.error(error);

        showToast("Approval request failed");

    }

}


async function payBill(encodedName) {

    const billName = decodeURIComponent(encodedName);

    const confirmed = confirm(
        `Execute payment for ${billName}?`
    );

    if (!confirmed) {
        return;
    }


    try {

        const response = await fetch(
            `/api/bill/${encodedName}/pay`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        document.getElementById("activityOutput").textContent =
            data.result;

        showToast(data.result);

        await loadDashboard();

    } catch (error) {

        console.error(error);

        showToast("Payment request failed");

    }

}


async function runLifeOps() {

    const button = document.getElementById("runButton");

    button.disabled = true;

    button.innerHTML = `
        <span>⟳</span>
        Running...
    `;


    document.getElementById("activityOutput").textContent =
        "LifeOps is investigating bills and evaluating payment safety...";


    try {

        const response = await fetch(
            `${API}/run`,
            {
                method: "POST"
            }
        );

        const data = await response.json();

        document.getElementById("activityOutput").textContent =
            data.result || "LifeOps workflow completed.";

        showToast("LifeOps workflow completed");

        await loadDashboard();

    } catch (error) {

        console.error(error);

        document.getElementById("activityOutput").textContent =
            `LifeOps error: ${error.message}`;

        showToast("LifeOps workflow failed");

    } finally {

        button.disabled = false;

        button.innerHTML = `
            <span>▶</span>
            Run LifeOps
        `;

    }

}


document
    .getElementById("runButton")
    .addEventListener(
        "click",
        runLifeOps
    );


loadDashboard();


// Refresh dashboard every 15 seconds.

setInterval(
    loadDashboard,
    15000
);
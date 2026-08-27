from typing import Optional

from pydantic import BaseModel


class Bill(BaseModel):
    id: int
    name: str
    amount: float
    currency: str
    due_date: str
    status: str
    decision: Optional[str] = None
    reason: Optional[str] = None
    payment_status: Optional[str] = None
    payment_reference: Optional[str] = None


class DashboardSummary(BaseModel):
    total_bills: int
    paid_count: int
    approval_count: int
    blocked_count: int
    total_paid: float
    awaiting_approval: float
    blocked_amount: float


class DashboardResponse(BaseModel):
    summary: DashboardSummary
    bills: list[Bill]


class ActionResponse(BaseModel):
    result: str


class WorkflowResponse(BaseModel):
    result: str
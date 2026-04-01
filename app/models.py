from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class QuoteRequest(BaseModel):
    accountId: str
    providerId: str
    modelId: str
    expectedRawQuantity: str
    metric: Literal["TOKEN_IN", "TOKEN_OUT", "SECOND", "REQUEST"]
    occurredAt: datetime


class QuoteResponse(BaseModel):
    quoteId: str
    computeUnitId: str
    billableQuantity: str
    unitPrice: str
    estimatedAmount: str
    expiresAt: datetime


class ConsumeRequest(BaseModel):
    authorizationId: str
    usageEventId: str
    actualRawQuantity: str
    actualBillableQuantity: str
    actualAmount: str
    traceId: str


class ConsumeResponse(BaseModel):
    usageEventId: str
    status: Literal["CONSUMED", "REJECTED"]
    consumedAmount: str
    releasedAmount: str
    ledgerVersion: int


class ReconcileRequest(BaseModel):
    accountId: str
    periodStart: datetime
    periodEnd: datetime
    providerStatementDigest: str


class ReconcileResponse(BaseModel):
    reconcileId: str
    status: Literal["MATCHED", "MISMATCH", "IN_PROGRESS"]
    invoiceId: str
    platformAmount: str
    providerAmount: str
    deltaAmount: str
    mismatchItems: int = 0


class AuditEvent(BaseModel):
    eventType: str
    eventId: str
    occurredAt: datetime
    signature: str


class AuditTrailResponse(BaseModel):
    traceId: str
    events: list[AuditEvent]
    chainHash: str


class ErrorDetail(BaseModel):
    code: str
    message: str
    requestId: str
    traceId: str
    retryable: bool


class ErrorEnvelope(BaseModel):
    error: ErrorDetail


class QuoteRecord(BaseModel):
    quote_id: str
    account_id: str
    provider_id: str
    model_id: str
    amount: str
    expires_at: datetime
    authorization_id: str


class UsageRecord(BaseModel):
    usage_event_id: str
    authorization_id: str
    trace_id: str
    amount: str
    occurred_at: datetime


class ReconcileRecord(BaseModel):
    reconcile_id: str
    account_id: str
    invoice_id: str
    platform_amount: str
    provider_amount: str
    delta_amount: str
    status: str = Field(default="MATCHED")

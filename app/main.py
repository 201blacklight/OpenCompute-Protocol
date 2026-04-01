from __future__ import annotations

import logging
from contextvars import ContextVar
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from app.models import (
    AuditTrailResponse,
    ConsumeRequest,
    ConsumeResponse,
    ErrorEnvelope,
    QuoteRequest,
    QuoteResponse,
    ReconcileRequest,
    ReconcileResponse,
)
from app.services import audit_trail, build_store, consume, quote, reconcile

app = FastAPI(title="OpenCompute MVP", version="0.1.0")
store = build_store()

request_id_ctx = ContextVar("request_id", default="-")
logger = logging.getLogger("opencompute")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s request_id=%(request_id)s message=%(message)s",
)

API_KEYS = {
    "mvp-admin-key": "admin",
    "mvp-ops-key": "ops",
    "mvp-auditor-key": "auditor",
}

ROLE_PERMISSIONS = {
    "admin": {"/api/v1/quote", "/api/v1/consume", "/api/v1/reconcile", "/api/v1/audit-trail"},
    "ops": {"/api/v1/quote", "/api/v1/consume", "/api/v1/reconcile"},
    "auditor": {"/api/v1/audit-trail"},
}


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        return True


logger.addFilter(RequestIdFilter())


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id", f"req_{uuid4().hex[:12]}")
    request_id_ctx.set(request_id)
    response = await call_next(request)
    response.headers["X-Request-Id"] = request_id
    return response


def enforce_access(path: str, api_key: str | None):
    if not api_key or api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="invalid api key")
    role = API_KEYS[api_key]
    if path not in ROLE_PERMISSIONS.get(role, set()):
        raise HTTPException(status_code=403, detail="permission denied")


def idempotent_response(idempotency_key: str | None):
    if idempotency_key and idempotency_key in store.idempotency:
        return store.idempotency[idempotency_key]
    return None


def save_idempotent_response(idempotency_key: str | None, payload: dict):
    if idempotency_key:
        store.idempotency[idempotency_key] = payload


@app.exception_handler(HTTPException)
async def http_exc_handler(_: Request, exc: HTTPException):
    body = ErrorEnvelope(
        error={
            "code": f"HTTP_{exc.status_code}",
            "message": str(exc.detail),
            "requestId": request_id_ctx.get(),
            "traceId": request_id_ctx.get(),
            "retryable": exc.status_code >= 500,
        }
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump())


@app.post("/api/v1/quote", response_model=QuoteResponse)
def quote_api(req: QuoteRequest, x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    enforce_access("/api/v1/quote", x_api_key)
    logger.info("quote.start")
    quote_record, provider_quote = quote(
        store=store,
        account_id=req.accountId,
        provider_id=req.providerId,
        model_id=req.modelId,
        expected_raw_quantity=req.expectedRawQuantity,
    )
    resp = QuoteResponse(
        quoteId=quote_record.quote_id,
        computeUnitId=provider_quote.compute_unit_id,
        billableQuantity=str(provider_quote.billable_quantity),
        unitPrice=str(provider_quote.unit_price),
        estimatedAmount=str(provider_quote.estimated_amount),
        expiresAt=quote_record.expires_at,
    )
    logger.info("quote.done")
    return resp


@app.post("/api/v1/consume", response_model=ConsumeResponse)
def consume_api(
    req: ConsumeRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    enforce_access("/api/v1/consume", x_api_key)
    cached = idempotent_response(idempotency_key)
    if cached:
        logger.info("consume.idempotent_hit")
        return cached

    logger.info("consume.start")
    payload = consume(
        store=store,
        authorization_id=req.authorizationId,
        usage_event_id=req.usageEventId,
        actual_amount=req.actualAmount,
        trace_id=req.traceId,
    )
    save_idempotent_response(idempotency_key, payload)
    logger.info("consume.done")
    return payload


@app.post("/api/v1/reconcile", response_model=ReconcileResponse)
def reconcile_api(
    req: ReconcileRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    enforce_access("/api/v1/reconcile", x_api_key)
    cached = idempotent_response(idempotency_key)
    if cached:
        logger.info("reconcile.idempotent_hit")
        return cached

    logger.info("reconcile.start")
    payload = reconcile(
        store=store,
        account_id=req.accountId,
        provider_statement_digest=req.providerStatementDigest,
    )
    save_idempotent_response(idempotency_key, payload)
    logger.info("reconcile.done")
    return payload


@app.get("/api/v1/audit-trail", response_model=AuditTrailResponse)
def audit_api(
    traceId: str,
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
):
    enforce_access("/api/v1/audit-trail", x_api_key)
    logger.info("audit.query")
    payload = audit_trail(store=store, trace_id=traceId)
    return payload


@app.get("/healthz")
def healthz():
    return {"status": "ok"}

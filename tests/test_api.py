from fastapi.testclient import TestClient

from app.main import app, store

client = TestClient(app)

ADMIN_HEADERS = {"X-API-Key": "mvp-admin-key"}
AUDITOR_HEADERS = {"X-API-Key": "mvp-auditor-key"}


def setup_function():
    store.idempotency.clear()
    store.quotes.clear()
    store.usage.clear()
    store.audit.clear()
    store.reconcile.clear()
    store.account_balances.clear()
    store.account_versions.clear()


def test_quote_success():
    resp = client.post(
        "/api/v1/quote",
        headers=ADMIN_HEADERS,
        json={
            "accountId": "acc_001",
            "providerId": "openai",
            "modelId": "gpt-4o-mini",
            "expectedRawQuantity": "100",
            "metric": "TOKEN_IN",
            "occurredAt": "2026-03-31T00:00:00Z",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["quoteId"].startswith("q_")
    assert data["computeUnitId"].startswith("cu-openai")


def test_consume_idempotent():
    body = {
        "authorizationId": "auth_001",
        "usageEventId": "usage_001",
        "actualRawQuantity": "100",
        "actualBillableQuantity": "100",
        "actualAmount": "0.2",
        "traceId": "trace_001",
    }
    headers = {**ADMIN_HEADERS, "Idempotency-Key": "idem-consume-1"}
    first = client.post("/api/v1/consume", headers=headers, json=body)
    second = client.post("/api/v1/consume", headers=headers, json=body)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()
    assert len(store.usage) == 1


def test_reconcile_idempotent():
    consume_body = {
        "authorizationId": "auth_001",
        "usageEventId": "usage_001",
        "actualRawQuantity": "100",
        "actualBillableQuantity": "100",
        "actualAmount": "0.2",
        "traceId": "acc_001",
    }
    client.post(
        "/api/v1/consume",
        headers={**ADMIN_HEADERS, "Idempotency-Key": "idem-c-pre"},
        json=consume_body,
    )
    req = {
        "accountId": "acc_001",
        "periodStart": "2026-03-01T00:00:00Z",
        "periodEnd": "2026-03-31T00:00:00Z",
        "providerStatementDigest": "ab00112233",
    }
    headers = {**ADMIN_HEADERS, "Idempotency-Key": "idem-r-1"}
    first = client.post("/api/v1/reconcile", headers=headers, json=req)
    second = client.post("/api/v1/reconcile", headers=headers, json=req)
    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json() == second.json()


def test_audit_permission():
    quote_resp = client.post(
        "/api/v1/quote",
        headers=ADMIN_HEADERS,
        json={
            "accountId": "acc_001",
            "providerId": "mock",
            "modelId": "base",
            "expectedRawQuantity": "50",
            "metric": "REQUEST",
            "occurredAt": "2026-03-31T00:00:00Z",
        },
    )
    assert quote_resp.status_code == 200

    quote_id = quote_resp.json()["quoteId"]
    trace_id = store.quotes[quote_id].authorization_id
    audit_resp = client.get("/api/v1/audit-trail", headers=AUDITOR_HEADERS, params={"traceId": trace_id})
    assert audit_resp.status_code == 200
    assert audit_resp.json()["traceId"] == trace_id
    assert len(audit_resp.json()["events"]) >= 1


def test_unauthorized_access():
    resp = client.post(
        "/api/v1/reconcile",
        headers={"X-API-Key": "mvp-auditor-key"},
        json={
            "accountId": "acc_001",
            "periodStart": "2026-03-01T00:00:00Z",
            "periodEnd": "2026-03-31T00:00:00Z",
            "providerStatementDigest": "ab00112233",
        },
    )
    assert resp.status_code == 403

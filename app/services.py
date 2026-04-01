from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from hashlib import sha256
from time import sleep
from uuid import uuid4

from app.models import AuditEvent, QuoteRecord, ReconcileRecord, UsageRecord
from app.providers import PROVIDERS, ProviderQuote


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_decimal(value: str) -> Decimal:
    return Decimal(value)


def _money_str(value: Decimal) -> str:
    return format(value.quantize(Decimal("0.00000001")), "f")


def retry_call(fn, max_attempts: int = 3, delay_s: float = 0.02):
    last_err = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except TimeoutError as err:
            last_err = err
            if attempt == max_attempts - 1:
                raise
            sleep(delay_s * (attempt + 1))
    raise last_err


def choose_provider(provider_id: str) -> str:
    if provider_id in PROVIDERS:
        return provider_id
    return "mock"


@dataclass
class InMemoryStore:
    idempotency: dict[str, dict]
    quotes: dict[str, QuoteRecord]
    usage: dict[str, UsageRecord]
    audit: dict[str, list[AuditEvent]]
    reconcile: dict[str, ReconcileRecord]
    account_balances: dict[str, Decimal]
    account_versions: dict[str, int]


def build_store() -> InMemoryStore:
    return InMemoryStore(
        idempotency={},
        quotes={},
        usage={},
        audit={},
        reconcile={},
        account_balances={},
        account_versions={},
    )


def append_audit(store: InMemoryStore, trace_id: str, event_type: str, event_id: str):
    events = store.audit.setdefault(trace_id, [])
    events.append(
        AuditEvent(
            eventType=event_type,
            eventId=event_id,
            occurredAt=_utc_now(),
            signature=sha256(f"{trace_id}:{event_id}:{event_type}".encode()).hexdigest(),
        )
    )


def quote(
    store: InMemoryStore,
    account_id: str,
    provider_id: str,
    model_id: str,
    expected_raw_quantity: str,
) -> tuple[QuoteRecord, ProviderQuote]:
    routed_provider = choose_provider(provider_id)
    provider = PROVIDERS[routed_provider]
    quantity = _to_decimal(expected_raw_quantity)
    provider_quote = retry_call(lambda: provider.quote(model_id=model_id, quantity=quantity))
    quote_id = f"q_{uuid4().hex[:12]}"
    authorization_id = f"auth_{uuid4().hex[:12]}"
    record = QuoteRecord(
        quote_id=quote_id,
        account_id=account_id,
        provider_id=routed_provider,
        model_id=model_id,
        amount=_money_str(provider_quote.estimated_amount),
        expires_at=_utc_now() + timedelta(minutes=10),
        authorization_id=authorization_id,
    )
    store.quotes[quote_id] = record
    append_audit(store, authorization_id, "QUOTE", quote_id)
    return record, provider_quote


def consume(
    store: InMemoryStore,
    authorization_id: str,
    usage_event_id: str,
    actual_amount: str,
    trace_id: str,
) -> dict:
    if usage_event_id in store.usage:
        usage = store.usage[usage_event_id]
        version = store.account_versions.get(trace_id, 1)
        return {
            "usageEventId": usage.usage_event_id,
            "status": "CONSUMED",
            "consumedAmount": usage.amount,
            "releasedAmount": "0.00000000",
            "ledgerVersion": version,
        }

    amount = _to_decimal(actual_amount)
    usage = UsageRecord(
        usage_event_id=usage_event_id,
        authorization_id=authorization_id,
        trace_id=trace_id,
        amount=_money_str(amount),
        occurred_at=_utc_now(),
    )
    store.usage[usage_event_id] = usage

    current = store.account_balances.get(trace_id, Decimal("0"))
    store.account_balances[trace_id] = current + amount
    version = store.account_versions.get(trace_id, 0) + 1
    store.account_versions[trace_id] = version
    append_audit(store, trace_id, "CONSUME", usage_event_id)
    return {
        "usageEventId": usage_event_id,
        "status": "CONSUMED",
        "consumedAmount": usage.amount,
        "releasedAmount": "0.00000000",
        "ledgerVersion": version,
    }


def reconcile(
    store: InMemoryStore,
    account_id: str,
    provider_statement_digest: str,
) -> dict:
    platform_amount = sum(
        (Decimal(rec.amount) for rec in store.usage.values()),
        start=Decimal("0"),
    )
    # Deterministic "provider amount" derived from digest to simulate reconciliation.
    digest_bias = Decimal(str((int(provider_statement_digest[:2], 16) % 3))) / Decimal("100")
    provider_amount = platform_amount + digest_bias
    delta = platform_amount - provider_amount
    reconcile_id = f"rec_{uuid4().hex[:12]}"
    invoice_id = f"inv_{uuid4().hex[:10]}"
    status = "MATCHED" if delta == 0 else "MISMATCH"
    rec = ReconcileRecord(
        reconcile_id=reconcile_id,
        account_id=account_id,
        invoice_id=invoice_id,
        platform_amount=_money_str(platform_amount),
        provider_amount=_money_str(provider_amount),
        delta_amount=_money_str(delta),
        status=status,
    )
    store.reconcile[reconcile_id] = rec
    append_audit(store, account_id, "RECONCILE", reconcile_id)
    return {
        "reconcileId": rec.reconcile_id,
        "status": rec.status,
        "invoiceId": rec.invoice_id,
        "platformAmount": rec.platform_amount,
        "providerAmount": rec.provider_amount,
        "deltaAmount": rec.delta_amount,
        "mismatchItems": 0 if status == "MATCHED" else 1,
    }


def audit_trail(store: InMemoryStore, trace_id: str) -> dict:
    events = store.audit.get(trace_id, [])
    chain = "|".join(f"{e.eventType}:{e.eventId}:{e.signature}" for e in events)
    chain_hash = sha256(chain.encode()).hexdigest() if chain else sha256(b"").hexdigest()
    return {
        "traceId": trace_id,
        "events": [e.model_dump() for e in events],
        "chainHash": chain_hash,
    }

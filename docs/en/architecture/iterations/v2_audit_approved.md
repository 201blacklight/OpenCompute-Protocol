# OCP Architecture v2 (Audit Approved)

## Critical Additions
- Ledger state machine with freeze/release/reversal/dispute flows.
- Idempotency + nonce + signature checks for all receipt-driven transitions.
- Double-entry style accounting events for traceability.
- Policy reporting interfaces for regulatory and pilot reporting.
- Sandbox SDKs for low-friction enterprise onboarding.

## Ledger States
- `INIT -> PENDING_RECEIPT`
- `PENDING_RECEIPT -> CREDITED | REJECTED`
- `CREDITED -> RESERVED -> CONSUMED`
- `RESERVED -> RELEASED`
- `CONSUMED -> REFUND_PENDING -> REFUNDED`
- `* -> DISPUTED -> RESOLVED`

## Acceptance Outcome
- Approved for demo implementation under non-custodial boundary.

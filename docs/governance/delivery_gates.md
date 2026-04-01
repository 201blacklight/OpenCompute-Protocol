# Delivery Gates

## G0 Initiation Gate
- Problem, boundary, non-goals, and legal assumptions are explicit.

## G1 Architecture Gate
- Security baseline, ledger consistency model, and rollback strategy are reviewed.

## G2 Demo Gate
- End-to-end flow works and audit events are reproducible.

## G3 Release Gate
- Docs, tests, scripts, and risk register are complete.

## Reject Conditions
- Missing idempotency or replay protection.
- Missing order-to-ledger traceability.
- Unhandled partial failures in settlement transitions.

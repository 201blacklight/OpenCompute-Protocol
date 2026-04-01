# OCP Architecture v1 Proposal

## Layered Components
- Gateway + Auth
- Token Exchange + Pricing
- Payment Receipt + Settlement
- Usage Ledger + Revenue Share Registry
- Payment/Model Adapters
- Audit + Risk

## Core Flow
1. External payment completed.
2. Receipt ingested and validated.
3. Token credits minted from exchange rate policy.
4. Model usage consumed with token deduction.
5. Revenue share booked to current beneficiary.

## Known Gaps in v1
- No anti-manipulation controls for pricing.
- Incomplete partial-failure reconciliation states.
- Weak dispute handling for rights transfer.

from __future__ import annotations

from typing import Dict, List, Tuple

from engine import OCPDemoEngine


def _format_table(headers: List[str], rows: List[List[str]]) -> str:
    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def line(sep: str = "-") -> str:
        return "+" + "+".join(sep * (w + 2) for w in widths) + "+"

    out = [line(), "| " + " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers)) + " |", line("=")]
    for row in rows:
        out.append("| " + " | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) + " |")
    out.append(line())
    return "\n".join(out)


def _snapshot_rows(snapshot: Dict[str, Dict[str, float]]) -> List[List[str]]:
    rows: List[List[str]] = []
    for account_id, data in sorted(snapshot.items()):
        rows.append([account_id, f"{data['cny']:.2f}", f"{data['token']:.2f}"])
    return rows


def _delta_rows(
    before: Dict[str, Dict[str, float]], after: Dict[str, Dict[str, float]]
) -> List[List[str]]:
    rows: List[List[str]] = []
    for account_id in sorted(after.keys()):
        b = before.get(account_id, {"cny": 0.0, "token": 0.0})
        a = after[account_id]
        rows.append(
            [
                account_id,
                f"{a['cny'] - b['cny']:+.2f}",
                f"{a['token'] - b['token']:+.2f}",
            ]
        )
    return rows


def _run_step(
    engine: OCPDemoEngine, step_name: str, action
) -> Tuple[Dict[str, Dict[str, float]], Dict[str, Dict[str, float]], List[str]]:
    before = engine.snapshot()
    prev_ledger_len = len(engine.ledger)
    action()
    after = engine.snapshot()
    events = [entry.event for entry in engine.ledger[prev_ledger_len:]]
    print(f"\n### {step_name}")
    print("Account Delta:")
    print(_format_table(["Account", "Delta CNY", "Delta Token"], _delta_rows(before, after)))
    print("Current Snapshot:")
    print(_format_table(["Account", "CNY", "Token"], _snapshot_rows(after)))
    if events:
        print("Events:", " -> ".join(events))
    return before, after, events


def run_visual_preview() -> None:
    print("\n=== OCP Visual Preview ===")
    print("Flow: receipt -> mint -> consume -> share transfer -> dispute freeze\n")
    engine = OCPDemoEngine(base_rate=12.0, dynamic_factor=1.05)

    _run_step(engine, "Step 0 - Create accounts", lambda: [
        engine.create_account("user_alice"),
        engine.create_account("provider_x"),
        engine.create_account("investor_y"),
    ])

    _run_step(
        engine,
        "Step 1 - Register model",
        lambda: engine.register_model(
            model_id="gpt-like-001",
            owner_account_id="provider_x",
            token_price_per_call=8.0,
            max_calls_quota=100,
        ),
    )

    _run_step(
        engine,
        "Step 2 - Payment receipt and token mint",
        lambda: engine.process_payment_receipt(
            account_id="user_alice", receipt_id="pay_001", cny_amount=50.0, nonce="n-100"
        ),
    )

    _run_step(
        engine,
        "Step 3 - First model usage (owner gets revenue)",
        lambda: engine.consume_model(user_account_id="user_alice", model_id="gpt-like-001", call_count=3),
    )

    _run_step(
        engine,
        "Step 4 - Transfer revenue share right",
        lambda: engine.transfer_revenue_share(
            model_id="gpt-like-001", new_beneficiary_account_id="investor_y"
        ),
    )

    _run_step(
        engine,
        "Step 5 - Second usage (new beneficiary gets revenue)",
        lambda: engine.consume_model(user_account_id="user_alice", model_id="gpt-like-001", call_count=2),
    )

    _run_step(
        engine,
        "Step 6 - Set dispute flag",
        lambda: engine.set_dispute(model_id="gpt-like-001", disputed=True),
    )

    _run_step(
        engine,
        "Step 7 - Third usage (revenue frozen)",
        lambda: engine.consume_model(user_account_id="user_alice", model_id="gpt-like-001", call_count=1),
    )

    print("\n=== Timeline ===")
    for i, e in enumerate(engine.ledger, start=1):
        print(f"{i:02d}. {e.event:<32} | ref={e.ref:<12} | detail={e.detail}")
    print("\n=== Final Snapshot ===")
    print(_format_table(["Account", "CNY", "Token"], _snapshot_rows(engine.snapshot())))


if __name__ == "__main__":
    run_visual_preview()

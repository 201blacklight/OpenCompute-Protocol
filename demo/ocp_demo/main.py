from engine import OCPDemoEngine


def run_demo() -> None:
    engine = OCPDemoEngine(base_rate=12.0, dynamic_factor=1.05)
    engine.create_account("user_alice")
    engine.create_account("provider_x")
    engine.create_account("investor_y")

    engine.register_model(
        model_id="gpt-like-001",
        owner_account_id="provider_x",
        token_price_per_call=8.0,
        max_calls_quota=100,
    )

    minted = engine.process_payment_receipt(
        account_id="user_alice", receipt_id="pay_001", cny_amount=50.0, nonce="n-100"
    )
    engine.consume_model(user_account_id="user_alice", model_id="gpt-like-001", call_count=3)
    engine.transfer_revenue_share(model_id="gpt-like-001", new_beneficiary_account_id="investor_y")
    engine.consume_model(user_account_id="user_alice", model_id="gpt-like-001", call_count=2)
    engine.set_dispute(model_id="gpt-like-001", disputed=True)
    engine.consume_model(user_account_id="user_alice", model_id="gpt-like-001", call_count=1)

    print("Minted token:", round(minted, 2))
    print("Snapshot:", engine.snapshot())
    print("Ledger events:", len(engine.ledger))
    for e in engine.ledger[-5:]:
        print(f"- {e.event} | {e.ref} | {e.detail}")


if __name__ == "__main__":
    run_demo()

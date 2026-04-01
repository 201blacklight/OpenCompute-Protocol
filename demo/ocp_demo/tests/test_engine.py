import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from engine import OCPDemoEngine


def test_receipt_idempotency():
    engine = OCPDemoEngine(base_rate=10.0, dynamic_factor=1.0)
    engine.create_account("u1")
    minted_1 = engine.process_payment_receipt("u1", "r1", 10.0, "n1")
    minted_2 = engine.process_payment_receipt("u1", "r1", 10.0, "n1")
    assert minted_1 == 100.0
    assert minted_2 == 0.0
    assert engine.accounts["u1"].token_balance == 100.0


def test_consume_and_revenue_share_transfer():
    engine = OCPDemoEngine(base_rate=10.0, dynamic_factor=1.0)
    engine.create_account("user")
    engine.create_account("owner")
    engine.create_account("investor")
    engine.register_model("m1", "owner", token_price_per_call=5.0, max_calls_quota=10)
    engine.process_payment_receipt("user", "r1", 10.0, "n1")
    engine.consume_model("user", "m1", 2)
    assert engine.accounts["owner"].token_balance == 10.0
    engine.transfer_revenue_share("m1", "investor")
    engine.consume_model("user", "m1", 2)
    assert engine.accounts["investor"].token_balance == 10.0


def test_dispute_freezes_distribution():
    engine = OCPDemoEngine(base_rate=10.0, dynamic_factor=1.0)
    engine.create_account("user")
    engine.create_account("owner")
    engine.register_model("m1", "owner", token_price_per_call=4.0, max_calls_quota=10)
    engine.process_payment_receipt("user", "r1", 10.0, "n1")
    engine.set_dispute("m1", True)
    engine.consume_model("user", "m1", 1)
    assert engine.accounts["owner"].token_balance == 0.0

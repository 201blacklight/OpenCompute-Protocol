from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class LedgerEntry:
    event: str
    ref: str
    detail: Dict[str, str]


@dataclass
class Account:
    account_id: str
    cny_balance: float = 0.0
    token_balance: float = 0.0


@dataclass
class ModelAsset:
    model_id: str
    owner_account_id: str
    token_price_per_call: float
    max_calls_quota: int
    used_calls: int = 0


@dataclass
class RevenueShareRight:
    model_id: str
    beneficiary_account_id: str
    share_ratio: float
    disputed: bool = False


@dataclass
class OCPDemoEngine:
    base_rate: float = 10.0
    dynamic_factor: float = 1.0
    idempotency_seen: set = field(default_factory=set)
    accounts: Dict[str, Account] = field(default_factory=dict)
    models: Dict[str, ModelAsset] = field(default_factory=dict)
    shares: Dict[str, RevenueShareRight] = field(default_factory=dict)
    ledger: List[LedgerEntry] = field(default_factory=list)

    def create_account(self, account_id: str, cny_balance: float = 0.0) -> None:
        if account_id in self.accounts:
            raise ValueError(f"account already exists: {account_id}")
        self.accounts[account_id] = Account(account_id=account_id, cny_balance=cny_balance)
        self._log("ACCOUNT_CREATED", account_id, {"cny_balance": f"{cny_balance:.2f}"})

    def register_model(
        self, model_id: str, owner_account_id: str, token_price_per_call: float, max_calls_quota: int
    ) -> None:
        if owner_account_id not in self.accounts:
            raise ValueError("owner account not found")
        self.models[model_id] = ModelAsset(
            model_id=model_id,
            owner_account_id=owner_account_id,
            token_price_per_call=token_price_per_call,
            max_calls_quota=max_calls_quota,
        )
        self.shares[model_id] = RevenueShareRight(
            model_id=model_id, beneficiary_account_id=owner_account_id, share_ratio=1.0
        )
        self._log("MODEL_REGISTERED", model_id, {"owner": owner_account_id})

    def process_payment_receipt(
        self, account_id: str, receipt_id: str, cny_amount: float, nonce: str
    ) -> float:
        key = f"{receipt_id}:{nonce}"
        if key in self.idempotency_seen:
            self._log("RECEIPT_DUPLICATE_IGNORED", receipt_id, {"account_id": account_id})
            return 0.0
        self.idempotency_seen.add(key)

        account = self._must_account(account_id)
        account.cny_balance += cny_amount
        minted = cny_amount * self.base_rate * self.dynamic_factor
        account.token_balance += minted
        self._log(
            "TOKEN_MINTED_BY_RECEIPT",
            receipt_id,
            {"account_id": account_id, "minted_token": f"{minted:.2f}"},
        )
        return minted

    def consume_model(self, user_account_id: str, model_id: str, call_count: int = 1) -> float:
        user = self._must_account(user_account_id)
        model = self._must_model(model_id)
        if model.used_calls + call_count > model.max_calls_quota:
            raise ValueError("quota exceeded")

        total_cost = model.token_price_per_call * call_count
        if user.token_balance < total_cost:
            raise ValueError("insufficient token")

        user.token_balance -= total_cost
        model.used_calls += call_count

        right = self.shares[model_id]
        if right.disputed:
            self._log("REVENUE_FROZEN_DUE_TO_DISPUTE", model_id, {"amount": f"{total_cost:.2f}"})
        else:
            beneficiary = self._must_account(right.beneficiary_account_id)
            beneficiary.token_balance += total_cost * right.share_ratio
            self._log(
                "REVENUE_SHARED",
                model_id,
                {
                    "beneficiary": right.beneficiary_account_id,
                    "amount": f"{total_cost * right.share_ratio:.2f}",
                },
            )

        self._log(
            "MODEL_CONSUMED",
            model_id,
            {"user": user_account_id, "call_count": str(call_count), "cost": f"{total_cost:.2f}"},
        )
        return total_cost

    def transfer_revenue_share(self, model_id: str, new_beneficiary_account_id: str) -> None:
        if new_beneficiary_account_id not in self.accounts:
            raise ValueError("new beneficiary not found")
        right = self.shares[model_id]
        old = right.beneficiary_account_id
        right.beneficiary_account_id = new_beneficiary_account_id
        self._log(
            "REVENUE_SHARE_TRANSFERRED",
            model_id,
            {"old_beneficiary": old, "new_beneficiary": new_beneficiary_account_id},
        )

    def set_dispute(self, model_id: str, disputed: bool) -> None:
        right = self.shares[model_id]
        right.disputed = disputed
        self._log("REVENUE_SHARE_DISPUTE_CHANGED", model_id, {"disputed": str(disputed)})

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        return {
            a.account_id: {"cny": round(a.cny_balance, 2), "token": round(a.token_balance, 2)}
            for a in self.accounts.values()
        }

    def _must_account(self, account_id: str) -> Account:
        if account_id not in self.accounts:
            raise ValueError(f"account not found: {account_id}")
        return self.accounts[account_id]

    def _must_model(self, model_id: str) -> ModelAsset:
        if model_id not in self.models:
            raise ValueError(f"model not found: {model_id}")
        return self.models[model_id]

    def _log(self, event: str, ref: str, detail: Dict[str, str]) -> None:
        self.ledger.append(LedgerEntry(event=event, ref=ref, detail=detail))

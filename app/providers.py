from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from random import random
from time import sleep


@dataclass
class ProviderQuote:
    unit_price: Decimal
    compute_unit_id: str
    billable_quantity: Decimal
    estimated_amount: Decimal


class BaseProviderClient:
    provider_id: str

    def quote(self, model_id: str, quantity: Decimal) -> ProviderQuote:
        raise NotImplementedError


class MockProviderClient(BaseProviderClient):
    provider_id = "mock"

    def quote(self, model_id: str, quantity: Decimal) -> ProviderQuote:
        unit_price = Decimal("0.001")
        return ProviderQuote(
            unit_price=unit_price,
            compute_unit_id=f"cu-{self.provider_id}-{model_id}",
            billable_quantity=quantity,
            estimated_amount=unit_price * quantity,
        )


class OpenAIProviderClient(BaseProviderClient):
    provider_id = "openai"

    def quote(self, model_id: str, quantity: Decimal) -> ProviderQuote:
        unit_price = Decimal("0.002")
        return ProviderQuote(
            unit_price=unit_price,
            compute_unit_id=f"cu-{self.provider_id}-{model_id}",
            billable_quantity=quantity,
            estimated_amount=unit_price * quantity,
        )


class AnthropicProviderClient(BaseProviderClient):
    provider_id = "anthropic"

    def quote(self, model_id: str, quantity: Decimal) -> ProviderQuote:
        # Simulate occasional transient provider failures.
        if random() < 0.15:
            raise TimeoutError("provider timeout")
        sleep(0.01)
        unit_price = Decimal("0.0025")
        return ProviderQuote(
            unit_price=unit_price,
            compute_unit_id=f"cu-{self.provider_id}-{model_id}",
            billable_quantity=quantity,
            estimated_amount=unit_price * quantity,
        )


PROVIDERS: dict[str, BaseProviderClient] = {
    "mock": MockProviderClient(),
    "openai": OpenAIProviderClient(),
    "anthropic": AnthropicProviderClient(),
}

from __future__ import annotations

import importlib
import os
from typing import Iterable

from techtest.models import PricingEngine, ResultReceiver, Trade
from techtest.risk_system.pricing_config_loader import PricingConfigLoader


class LoadPricerError(Exception):
    """Raised when _load_pricers fails."""


class SerialPricer:
    def __init__(self) -> None:
        self._pricers: dict[str, PricingEngine] = {}

    def price(self, trade_containers: Iterable[Iterable[Trade]], result_receiver: ResultReceiver) -> None:
        self._load_pricers()

        for trade_container in trade_containers:
            for trade in trade_container:
                if trade.trade_type not in self._pricers:
                    result_receiver.add_error(trade.trade_id, "No Pricing Engines available for this trade type")
                    continue

                pricer = self._pricers[trade.trade_type]
                pricer.price(trade, result_receiver)

    def _load_pricers(self) -> None:
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "pricing_config",
            "PricingEngines.xml",
        )
        pricing_config_loader = PricingConfigLoader()
        pricing_config_loader.config_file = config_path
        try:
            pricer_config = pricing_config_loader.load_config()
        except Exception as exc:  # XML parse errors, IO errors, schema errors
            raise LoadPricerError(f"Failed to parse {config_path}: {exc}") from exc

        if not pricer_config:
            raise LoadPricerError(f"No pricers defined in {config_path}")

        for config_item in pricer_config:
            module = importlib.import_module(config_item.module)
            engine_class = getattr(module, config_item.class_name)
            self._pricers[config_item.trade_type] = engine_class()

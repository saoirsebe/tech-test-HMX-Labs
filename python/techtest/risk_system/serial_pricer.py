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

        pricers = {}

        for config_item in pricer_config:
            config_item_label = f"Trade type: {config_item.trade_type} ({config_item.module}.{config_item.class_name})"

            if not (config_item.trade_type and config_item.module and config_item.class_name):
                raise LoadPricerError(f"Incomplete config item: {config_item_label}")

            # Duplicate trade types
            if config_item.trade_type in pricers:
                continue

            try:
                module = importlib.import_module(config_item.module)
            except AttributeError as exc:
                raise LoadPricerError(f"Cannot import module for {config_item_label}: {exc}")

            engine_class = getattr(module, config_item.class_name)
            if not callable(engine_class):
                raise TypeError(f"{config_item.class_name} is not callable")

            try:
                pricers[config_item.trade_type] = engine_class()
            except Exception as exc:
                raise LoadPricerError(f"Cannot instantiate {config_item_label}: {exc}")

        self._pricers.update(pricers)


from __future__ import annotations

import importlib
from typing import Iterable

from techtest.models import PricingEngine, ResultReceiver, Trade
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from techtest.risk_system.pricing_config_loader import PricingConfigLoader
from techtest.risk_system.serial_pricer import LoadPricerError


class ParallelPricer:
    def __init__(self) -> None:
        self._pricers: dict[str, PricingEngine] = {}

    def price(self, trade_containers: Iterable[Iterable[Trade]], result_receiver: ResultReceiver) -> None:
        # Input validation
        if trade_containers is None:
            raise ValueError("trade_containers must not be None")
        if result_receiver is None:
            raise ValueError("result_receiver must not be None")
        if isinstance(trade_containers, (str, bytes)):
            raise TypeError("trade_containers must be an iterable of trade containers, not a string")

        self._load_pricers()

        with ThreadPoolExecutor() as executor:
            futures = {}
            for trade_container in trade_containers:
                if trade_container is None:
                    continue
                for trade in trade_container:
                    if trade is None:
                        continue
                    if trade.trade_type not in self._pricers:
                        result_receiver.add_error(trade.trade_id, "No Pricing Engines available for this trade type")
                        continue

                    pricer = self._pricers[trade.trade_type]
                    future = executor.submit(pricer.price, trade, result_receiver)
                    futures[future] = trade

            # Block until every pricing call has finished, collect in order of completion
            for future in as_completed(futures):
                trade = futures[future]
                try:
                    future.result()
                except Exception as exc:
                    # One failure won't prevent the remaining pricing calls from completing.
                    result_receiver.add_error(trade.trade_id, f"Pricing failed: {exc}")

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
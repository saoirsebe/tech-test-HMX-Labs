from __future__ import annotations
from typing import Iterable
from techtest.risk_system import PricingEngineConfigItem
import xml.etree.ElementTree as ET


class PricingConfigLoader:
    def __init__(self) -> None:
        self.config_file: str | None = None

    def load_config(self) -> Iterable[PricingEngineConfigItem]:
        engine_list = []

        self._load_engines_from_file(self.config_file, engine_list)

        return engine_list

    def _create_price_engine_from_engine(self, engine:ET.Element) -> PricingEngineConfigItem:
        trade_type = engine.get("tradeType")
        module = engine.get("module")
        class_name = engine.get("class")

        if not all([trade_type, module, class_name]):
            raise ValueError("Invalid pricing engine configuration")

        return PricingEngineConfigItem(
            trade_type=trade_type,
            module=module,
            class_name=class_name
        )

    def _load_engines_from_file(self, filename: str, engine_list: list[PricingEngineConfigItem]) -> None:
        tree = ET.parse(filename)
        root = tree.getroot()

        for engine in root.findall("Engine"):
            engine_list.append(self._create_price_engine_from_engine(engine))

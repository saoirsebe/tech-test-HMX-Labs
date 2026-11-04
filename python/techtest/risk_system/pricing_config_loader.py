from __future__ import annotations
from techtest.risk_system import PricingEngineConfigItem
import xml.etree.ElementTree as ET


class PricingConfigLoader:
    def __init__(self) -> None:
        self.config_file: str | None = None

    def load_config(self) -> list[PricingEngineConfigItem]:
        if self.config_file is None:
            raise ValueError("No configuration file provided")

        return self._load_engines_from_file(self.config_file)


    def _create_price_engine_from_engine(self, engine:ET.Element) -> PricingEngineConfigItem:
        trade_type = engine.get("tradeType")
        module = engine.get("module")
        class_name = engine.get("class")

        if not all((trade_type, module, class_name)):
            raise ValueError("Invalid pricing engine configuration")

        return PricingEngineConfigItem(
            trade_type=trade_type,
            module=module,
            class_name=class_name
        )

    def _load_engines_from_file(self, filename: str) -> list[PricingEngineConfigItem]:
        tree = ET.parse(filename)
        root = tree.getroot()

        return [self._create_price_engine_from_engine(engine)
        for engine in root.findall("Engine")]

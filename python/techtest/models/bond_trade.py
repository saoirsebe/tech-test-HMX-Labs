from __future__ import annotations

from techtest.models.base_trade import BaseTrade


class BondTrade(BaseTrade):
    GOV_BOND_TRADE_TYPE = "GovBond"
    CORP_BOND_TRADE_TYPE = "CorpBond"
    SUPRA_BOND_TRADE_TYPE = "Supra" # New type to support item 10 in BondTrades.dat

    def __init__(self, trade_id: str, trade_type: str) -> None:
        super().__init__()
        if trade_id is None or not trade_id.strip():
            raise ValueError("A valid non null, non empty trade ID must be provided")

        if trade_type not in (
            self.GOV_BOND_TRADE_TYPE,
            self.CORP_BOND_TRADE_TYPE,
            self.SUPRA_BOND_TRADE_TYPE
        ):
            raise ValueError("Invalid bond trade type")

        self._trade_id = trade_id
        self._trade_type = trade_type

    @property
    def trade_type(self) -> str:
        return self._trade_type

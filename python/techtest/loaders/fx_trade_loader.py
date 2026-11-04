from __future__ import annotations

from datetime import datetime
from typing import Iterable

from techtest.models import Trade, FxTrade, FxTradeList


class FxTradeLoader:
    _SEPARATOR = "¬"
    def __init__(self, data_file: str) -> None:
        self.data_file = data_file

    # NOTE: This method is only here to allow the solution to run prior to the test being completed.
    def load_trades(self) -> Iterable[Trade]:
        trade_list = FxTradeList()

        self._load_trades_from_file(self.data_file, trade_list)

        return trade_list


    def _create_trade_from_line(self, line: str) -> FxTrade:
        items = line.split(self._SEPARATOR)
        trade = FxTrade(items[8], items[0])
        trade.trade_date = datetime.fromisoformat(items[1])
        trade.instrument = items[2] + items[3]
        trade.counterparty = items[7]
        trade.notional = float(items[4])
        trade.rate = float(items[5])
        trade.value_date = datetime.fromisoformat(items[6])

        return trade

    def _load_trades_from_file(self, filename: str, trade_list: FxTradeList) -> None:

        # utf-8-sig skips the byte order mark at the start of the file
        with open(filename, encoding="utf-8-sig") as stream:
            next(stream, None)  # Skip the header line
            next(stream, None)  # Skip the header line

            for line in stream:
                if line.startswith("END"):
                        continue

                trade_list.add(self._create_trade_from_line(line.rstrip("\r\n")))
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Iterator

from techtest.models import Trade, FxTrade, FxTradeList


class FxTradeLoader:
    _SEPARATOR = "¬"
    def __init__(self, data_file: str) -> None:
        self.data_file = data_file

    def load_trades(self) -> Iterable[Trade]:
        # Only one trade is held at a time
        yield from self._load_trades_from_file(self.data_file)


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

    def _load_trades_from_file(self, filename: str) -> Iterator[FxTrade]:

        # utf-8-sig skips the byte order mark at the start of the file
        with open(filename, encoding="utf-8-sig") as stream:
            next(stream, None)  # Skip the header line
            next(stream, None)  # Skip the header line

            for line in stream:
                if line.startswith("END"):
                        continue

                yield self._create_trade_from_line(line.rstrip("\r\n"))
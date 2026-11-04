from __future__ import annotations

from techtest.models import ScalarResults


class ScreenResultPrinter:
    def print_results(self, results: ScalarResults) -> None:
        for result in results:
            trade_id = result.trade_id

            if result.result is not None and result.error is not None:
                print(f"{trade_id} : {result.result} : {result.error}")

            elif result.error is not None:
                print(f"{trade_id} : {result.error}")

            elif result.result is not None:
                print(f"{trade_id} : {result.result}")

            pass

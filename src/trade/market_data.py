import itertools
from time import sleep

from wazirx.rest.client import Client

from trade.symbol import symbol_list

from .exception import MissingAttributeError


class MarketData:
    def __init__(self, api_key=None, api_secret=None):
        if not api_key:
            raise MissingAttributeError("api_key required")
        if not api_secret:
            raise MissingAttributeError("api_secret required")

        self.client = Client(api_key=api_key, secret_key=api_secret)
        self.filtered_asset = {}

    def chart_24hr(self):
        return self.client.send("tickers")

    def symbol_chart_24hr(self, symbol=None):
        if not symbol:
            raise MissingAttributeError("symbol required")

        return self.client.send("ticker", {"symbol": symbol})

    def trades(self, symbol, trade_limit):
        if not symbol:
            raise MissingAttributeError("symbol required")
        if not trade_limit:
            raise MissingAttributeError("trade_limit required")

        return self.client.send("trades", {"symbol": symbol,
                                           "limit": trade_limit})

    def get_symbol_depth(self, symbol=None, trade_limit=None):
        if not symbol:
            raise MissingAttributeError("symbol required")
        if not trade_limit:
            raise MissingAttributeError("trade_limit required")

        return self.client.send("depth", {"symbol": symbol,
                                          "limit": trade_limit})

    def symbol_depth_calculator(self, buy, sell):
        return ((sell - buy) / buy) * 100

    def process_symbol(self, amount_limit=None, symbol_limit=None, depth_limit=None):

        if not amount_limit:
            raise MissingAttributeError("amount_limit required")

        if not symbol_limit:
            raise MissingAttributeError("symbol_limit required")

        if not depth_limit:
            raise MissingAttributeError("depth_limit required")

        unsorted_symbols = {}
        for symbol in symbol_list:
            sleep(1)
            depth = self.get_symbol_depth(symbol, 1)
            try:
                sell = float(depth[1]["asks"][0][0])
                buy = float(depth[1]["bids"][0][0])

                depth_percentage = self.symbol_depth_calculator(buy, sell)

                if depth_percentage >= depth_limit:
                    unsorted_symbols[symbol] = {"depth": depth_percentage,
                                                "buy": buy,
                                                "sell": sell}
            except Exception:
                pass

        self.filtered_asset = dict(sorted(unsorted_symbols.items(),
                                          key=lambda x: x[1]['depth'], reverse=True))

        self.filtered_asset = dict(filter(lambda item:
                                          item[1]["buy"] < amount_limit,
                                          self.filtered_asset.items()))

        self.filtered_asset = dict(itertools.islice(
            self.filtered_asset.items(), symbol_limit))

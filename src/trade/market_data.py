import itertools
from time import sleep

from wazirx.rest.client import Client

from .exception import MissingAttributeError


class MarketData:
    def __init__(self, api_key=None, api_secret=None):
        if not api_key:
            raise MissingAttributeError("api_key required")
        if not api_secret:
            raise MissingAttributeError("api_secret required")

        self.client = Client(api_key=api_key, secret_key=api_secret)
        self.filtered_asset = {}

    def validate(self,
                 get_symbol_depth=None, symbol=None, limit=None,
                 process_symbol=None, apply_filter=None, symbols=None, amount_limit=None, symbol_limit=None, depth_limit=None):

        if process_symbol:
            if symbols:
                if not type(symbols) is list:
                    raise TypeError(
                        f"Expected a list for 'symbols' but received a {type(symbols).__name__}.")
            if apply_filter:
                if not amount_limit:
                    raise MissingAttributeError("amount_limit required")
                else:
                    if not type(amount_limit) is int:
                        raise TypeError(
                            f"Expected a int for 'amount_limit' but received a {type(amount_limit).__name__}.")

                if not symbol_limit:
                    raise MissingAttributeError("symbol_limit required")
                else:
                    if not type(symbol_limit) is int:
                        raise TypeError(
                            f"Expected a int for 'symbol_limit' but received a {type(symbol_limit).__name__}.")

                if not depth_limit:
                    raise MissingAttributeError("depth_limit required")
                else:
                    if not type(depth_limit) is int:
                        raise TypeError(
                            f"Expected a int for 'depth_limit' but received a {type(depth_limit).__name__}.")

        else:
            if not symbol:
                raise MissingAttributeError("symbol required")
            else:
                if not type(symbol) is str:
                    raise TypeError(
                        f"Expected a str for 'symbol' but received a {type(symbol).__name__}.")

            if get_symbol_depth:
                if not limit:
                    raise MissingAttributeError("limit required")
                else:
                    if not type(limit) is int:
                        raise TypeError(
                            f"Expected a int for 'limit' but received a {type(limit).__name__}.")

    def chart_24hr(self):
        return self.client.send("tickers")

    def symbol_chart_24hr(self, symbol=None):
        self.validate(symbol=symbol)

        return self.client.send("ticker", {"symbol": symbol})

    def trades(self, symbol, trade_limit):
        self.validate(symbol=symbol, )

        return self.client.send("trades", {"symbol": symbol,
                                           "limit": trade_limit})

    def get_symbol_depth(self, symbol=None, limit=None):
        self.validate(symbol=symbol, get_symbol_depth=True, limit=limit)

        return self.client.send("depth", {"symbol": symbol,
                                          "limit": limit})

    def symbol_depth_calculator(self, buy, sell):
        return ((sell - buy) / buy) * 100

    def process_symbol(self, symbols=None, apply_filter=None, amount_limit=None, symbol_limit=None, depth_limit=None):

        self.validate(process_symbol=True, symbols=symbols, apply_filter=apply_filter, amount_limit=amount_limit,
                      symbol_limit=symbol_limit, depth_limit=depth_limit)

        if symbols is not None:
            symbol_list = symbols
        else:
            from trade.symbol import symbol_list

        self.filtered_asset = {}
        for symbol in symbol_list:
            sleep(1)
            depth = self.get_symbol_depth(symbol, 1)
            try:
                sell = float(depth[1]["asks"][0][0])
                buy = float(depth[1]["bids"][0][0])

                depth_percentage = self.symbol_depth_calculator(buy, sell)
                if apply_filter:
                    if depth_percentage >= depth_limit:
                        self.filtered_asset[symbol] = {"depth": depth_percentage,
                                                       "buy": buy,
                                                       "sell": sell}
                else:
                    self.filtered_asset[symbol] = {"depth": depth_percentage,
                                                   "buy": buy,
                                                   "sell": sell}
            except Exception:
                pass

        # print(self.filtered_asset)
        if apply_filter:
            self.filtered_asset = dict(sorted(self.filtered_asset.items(),
                                              key=lambda x: x[1]['depth'], reverse=True))

            self.filtered_asset = dict(filter(lambda item:
                                              item[1]["buy"] < amount_limit,
                                              self.filtered_asset.items()))

            self.filtered_asset = dict(itertools.islice(
                self.filtered_asset.items(), symbol_limit))

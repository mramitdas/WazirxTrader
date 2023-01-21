from wazirx.rest.client import Client
from src.trade.coins import coins
from time import sleep


class MarketData:
    def __init__(self, api_key=None, api_secret=None,
                 symbol=None, limit=None, depth_limit=None):
        self.client = Client(api_key=api_key, secret_key=api_secret)
        self.symbol = {}

        if depth_limit:
            self.depth_limit = depth_limit
        else:
            self.depth_limit = 5

    def chart_24hr(self):
        return self.client.send("tickers")

    def symbol_chart_24hr(self, symbol):
        return self.client.send("ticker", {"symbol": symbol})

    def trades(self, symbol, limit):
        return self.client.send("trades", {"symbol": symbol,
                                           "limit": limit})

    def depth(self, symbol, limit):
        return self.client.send("depth", {"symbol": symbol,
                                          "limit": limit})

    def depth_cal(self, buy, sell):
        return ((sell - buy) / buy) * 100

    def coin_depth(self):
        unsorted_coin = {}
        for coin in coins:
            sleep(1)
            depth = self.depth(coin, 1)
            try:
                sell = depth[1]["asks"][0][0]
                buy = depth[1]["bids"][0][0]

                depth_percentage = self.depth_cal(float(buy), float(sell))

                if depth_percentage >= self.depth_limit:
                    unsorted_coin[coin] = {"depth": depth_percentage}
            except Exception:
                pass

        self.symbol = dict(sorted(unsorted_coin.items(),
                                  key=lambda x: x[1]['depth'], reverse=True))

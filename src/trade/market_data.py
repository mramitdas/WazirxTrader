from wazirx.rest.client import Client


class MarketData:
    def __init__(self, api_key=None, api_secret=None, symbol=None, limit=None):
        self.client = Client(api_key=api_key, secret_key=api_secret)

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

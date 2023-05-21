import itertools
import traceback
from collections import OrderedDict
from time import sleep

from wazirx.rest.client import Client

from .exception import MissingAttributeError
from .log import setup_logger


class MarketData:
    def __init__(self, api_key=None, api_secret=None):
        """_summary_

        Args:
            api_key (str): wazirx api key
            api_secret (str): wazirx secret key
        Returns:
            self.client: obj instance
            self.filtered_asset (dict): symbols qualified for trading
        """

        if not api_key:
            raise MissingAttributeError("api_key required")
        if not api_secret:
            raise MissingAttributeError("api_secret required")

        self.client = Client(api_key=api_key, secret_key=api_secret)
        self.filtered_asset = {}
        self.log = setup_logger()

    def validate(
        self,
        get_symbol_depth=None,
        symbol=None,
        limit=None,
        process_symbol=None,
        apply_filter=None,
        symbols=None,
        amount_limit=None,
        symbol_limit=None,
        depth_limit=None,
    ):
        """_summary_

        Acts as middleware (serializer)
        accepts multiple arguments and raise MissingAttributeError & TypeError if missing/invalid
        """
        if process_symbol:
            if symbols:
                if not isinstance(symbols, list):
                    raise TypeError(
                        f"Expected a list for 'symbols' but received a {type(symbols).__name__}."
                    )
            if apply_filter:
                if not amount_limit:
                    raise MissingAttributeError("amount_limit required")
                else:
                    if not isinstance(amount_limit, int):
                        raise TypeError(
                            f"Expected a int for 'amount_limit' but received a {type(amount_limit).__name__}."
                        )

                if not symbol_limit:
                    raise MissingAttributeError("symbol_limit required")
                else:
                    if not isinstance(symbol_limit, int):
                        raise TypeError(
                            f"Expected a int for 'symbol_limit' but received a {type(symbol_limit).__name__}."
                        )

                if not depth_limit:
                    raise MissingAttributeError("depth_limit required")
                else:
                    if not isinstance(depth_limit, int):
                        raise TypeError(
                            f"Expected a int for 'depth_limit' but received a {type(depth_limit).__name__}."
                        )

        else:
            if not symbol:
                raise MissingAttributeError("symbol required")
            else:
                if not isinstance(symbol, str):
                    raise TypeError(
                        f"Expected a str for 'symbol' but received a {type(symbol).__name__}."
                    )

            if get_symbol_depth:
                if not limit:
                    raise MissingAttributeError("limit required")
                else:
                    if not isinstance(limit, int):
                        raise TypeError(
                            f"Expected a int for 'limit' but received a {type(limit).__name__}."
                        )

    def symbol_chart_24hr(self, symbol=None):
        """_summary_

        24 hour rolling window price change statistics.

        Rate limit: 1 per second
        Args:
            symbol: crypto name
        Returns:
            dict: {}
        """
        if symbol:
            self.validate(symbol=symbol)
            return self.client.send("ticker", {"symbol": symbol})
        else:
            return self.client.send("tickers")

    def trades(self, symbol, limit):
        """_summary_

        Get recent trades.

        Rate limit: 1 per second
        Args:
            symbol: crypto name
            limit: no of records
        Returns:
            dict: {}
        """
        self.validate(symbol=symbol, get_symbol_depth=True, limit=limit)
        return self.client.send("trades", {"symbol": symbol, "limit": limit})

    def get_symbol_depth(self, symbol=None, limit=None):
        """_summary_

        Get symbol depth.

        Rate limit: 1 per second
        Args:
            symbol: crypto name
            limit: no of records
        Returns:
            dict: {}
        """
        self.validate(symbol=symbol, get_symbol_depth=True, limit=limit)
        return self.client.send("depth", {"symbol": symbol, "limit": limit})

    def symbol_depth_calculator(self, buy, sell):
        """_summary_

        Args:
            buy (float): asset buy price
            sell (float): asset sell price

        Returns:
            float: percentage at which profit can be booked
        """
        return ((sell - buy) / buy) * 100

    def process_symbol(
        self,
        symbols=None,
        apply_filter=None,
        amount_limit=None,
        symbol_limit=None,
        depth_limit=None,
    ):
        """_summary_
        The function will process and filter symbols, either those provided by the user or those found in a symbol file.
        The output will consist of the best symbols that were identified.

        Args:
            symbols (list, optional): cryptocurrencies that the user would like to trade
            apply_filter (bool, optional): If True, below filters will be applied
            amount_limit (int, optional): filters out cryptocurrencies based on their amount
            symbol_limit (int, optional): filters out the top performing cryptocurrencies
            depth_limit (int, optional): filters out cryptocurrencies based on their market depth
        """

        self.validate(
            process_symbol=True,
            symbols=symbols,
            apply_filter=apply_filter,
            amount_limit=amount_limit,
            symbol_limit=symbol_limit,
            depth_limit=depth_limit,
        )

        if symbols is not None:
            symbol_list = symbols
        else:
            from .symbol import Symbol
            symbol_list = Symbol().symbol_list

        self.filtered_asset = {}
        for symbol in symbol_list:
            depth = self.get_symbol_depth(symbol, 1)
            sleep(1)
            symbol_24hour_data = self.symbol_chart_24hr(symbol)
            try:
                volume = float(symbol_24hour_data[1]["volume"])
            except Exception:
                # exception occurs in case of newly listed symbol
                self.log.warning(traceback.format_exc())
                volume = 0
            try:
                sell = float(depth[1]["asks"][0][0])
                buy = float(depth[1]["bids"][0][0])

                depth_percentage = self.symbol_depth_calculator(buy, sell)
                if apply_filter:
                    if depth_percentage >= depth_limit:
                        self.filtered_asset[symbol] = {
                            "depth": depth_percentage,
                            "volume": volume,
                            "buy": buy,
                            "sell": sell,
                        }
                else:
                    self.filtered_asset[symbol] = {
                        "depth": depth_percentage,
                        "volume": volume,
                        "buy": buy,
                        "sell": sell,
                    }
            except Exception:
                self.log.error(traceback.format_exc())

        if apply_filter:
            self.filtered_asset = OrderedDict(
                sorted(
                    self.filtered_asset.items(),
                    key=lambda x: x[1]["volume"],
                    reverse=True,
                )
            )

            self.filtered_asset = OrderedDict(
                filter(
                    lambda item: item[1]["buy"] < amount_limit,
                    self.filtered_asset.items(),
                )
            )

            self.filtered_asset = OrderedDict(
                itertools.islice(self.filtered_asset.items(), symbol_limit)
            )

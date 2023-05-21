import threading
import traceback
from time import sleep

from trade.database import DataBase
from trade.market_data import MarketData
from trade.order import Order

from trade.log import setup_logger


class SpreadTrading:
    def __init__(self, api_key=None, api_secret=None, db_url=None, Test=False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.db_url = db_url

        self.test = Test
        self.order_id = 0

        self.market_data = MarketData(self.api_key, self.api_secret)
        self.order = Order(self.api_key, self.api_secret)
        self.db = DataBase(self.db_url)
        self.asset_list = {}
        self.trade_history = {}
        self.lock = threading.Lock()

        self.log = setup_logger()
        self.retrieve_assets()

    def retrieve_assets(self):
        """_summary_
        Retrieves the asset list from the 'asset' table in the 'wazirx' database and
        initializes the trade history for each asset.

        The function retrieves the asset list from the 'asset' table in the 'wazirx'
        database using the 'query' method of the 'db' object. The retrieved data is
        stored in the 'asset_list' attribute of the instance. The function also calls
        the 'init_trade_history' method to initialize the trade history for each asset.

        Args: NONE
        Returns: NONE
        """
        try:
            self.asset_list = self.db.query(
                db_name="wazirx", table_name="asset")["data"]
        except Exception:
            self.log.critical(traceback.format_exc())
            exit()
        # initiate trade history
        self.init_trade_history()

    def init_trade_history(self):
        """_summary_
        Initializes the trade history for each asset in the asset list.

        For each asset in the asset list, if it does not already exist in the trade history,
        a new entry is created with empty "buy" and "sell" dictionaries, as well as a "meta"
        dictionary with "buy_count" and "sell_count" keys initialized to zero.

        Args: NONE
        Returns: NONE
        """
        for asset in self.asset_list:
            if asset not in self.trade_history:
                self.trade_history[asset] = {
                    "buy": {},
                    "sell": {},
                    "meta": {"buy_count": 0, "sell_count": 0},
                }

    def asset_price_calculator(self, asset_price):
        """_summary_
        Calculates the price for an asset based on the given asset price.

        The function takes an asset price as input and calculates the price for the
        asset based on the following rules:

        - If the asset price has a decimal part, the function adds 1 to the integer
        part of the decimal and returns the resulting float value. If the decimal
        part starts with one or more zeroes, the function adds the same number of
        preceding zeroes to the decimal part of the result.
        - If the asset price does not have a decimal part, the function adds 0.1 to
        the integer part and returns the resulting float value.

        Args:
            asset_price (str or float): The price of the asset to calculate.

        Returns:
            float: The calculated price for the asset.
        """
        asset_price_split = asset_price.split(".")
        if len(asset_price_split) > 1:
            decimal_val = asset_price_split[1]
            zeros = ""
            if decimal_val.startswith("0"):
                preceding_zeros = decimal_val.count(
                    "0", 0, len(decimal_val) - len(decimal_val.lstrip("0"))
                )
                zeros = "".join(["0" for i in range(preceding_zeros)])
            return float(
                f"{asset_price_split[0]}.{zeros}{int(decimal_val) + 1}")
        else:
            return float(asset_price) + 0.1

    def trade_asset(self):
        """_summary_
        Trades each asset in the asset list by buying and selling it based on the current market depth.

        The function loops through each asset in the asset list and retrieves the current market depth
        using the 'get_symbol_depth' method of the 'market_data' object. If the market depth is retrieved
        successfully, the function calls the 'buy_asset' and 'sell_asset' methods of the instance with
        the corresponding bid and ask prices retrieved from the market depth.

        If the market depth retrieval or any of the trading operations fail, the function logs the
        exception message to the file and continues to the next asset.

        Args: NONE
        Returns: NONE
        """
        for asset in self.asset_list:
            try:
                sleep(1)
                depth = self.market_data.get_symbol_depth(
                    symbol=asset, limit=5)

                if depth[0] == 200:
                    self.buy_asset(
                        asset=asset,
                        buy_price=depth[1]["bids"][0][0],
                        rival_buy_price=depth[1]["bids"][1][0],
                    )

                    self.sell_asset(
                        asset=asset,
                        sell_price=depth[1]["asks"][0][0],
                        rival_sell_price=depth[1]["asks"][1][0],
                    )
            except Exception:
                self.log.error(traceback.format_exc())

    def remove_completed_orders(self, asset, type=None):
        """_summary_
        Removes completed orders of a specific type for a given asset from the trade history.

        The function first retrieves the order list of the specified type for the given asset from
        the trade history. If the order list exists, the function creates a copy of it and iterates
        over each order in the list. For each completed order, the function removes the order from the
        copy of the order list.

        Once all completed orders are removed, the function updates the trade history with the modified
        order list using a lock to ensure thread safety. The function returns both the original and the
        modified order list.

        If the specified type or asset does not exist in the trade history, the function returns empty
        dictionaries.

        Args:
            asset (str): The symbol of the asset to remove completed orders for.
            type (str, optional): The type of orders to remove (buy or sell).

        Returns:
            tuple: A tuple containing two dictionaries. The first dictionary contains the original
                order list, and the second dictionary contains the modified order list with completed
                orders removed.
        """
        order_list = self.trade_history[asset].get(type)
        if order_list is not None:
            order_list_copy = order_list.copy()

            for order in order_list:
                if order_list[order]["status"] is True:
                    del order_list_copy[order]

            with self.lock:
                self.trade_history[asset][type] = order_list_copy

            return order_list, order_list_copy
        return {}, {}

    def check_rival_orders(
            self,
            asset,
            type,
            current_price,
            rival_price,
            buy=True,
            completed_orders=None):
        """_summary_
        Compares the current market price of an asset against a rival price and the price of open orders
        associated with the asset, and cancels any orders that should be cancelled.

        Args:
            asset (str): The name of the asset to trade.
            type (str): The type of the order (either "buy" or "sell").
            current_price (str): The current market price of the asset.
            rival_price (str): The rival price to compare against the asset's price.
            buy (bool): Whether the order is a buy order (True) or a sell order (False).
            completed_orders (dict): A dictionary to store information about any completed orders that
            were cancelled.

        Returns:
            tuple: A tuple containing the number of orders that were cancelled, the final price to use
            for any new orders, and the dictionary of completed orders (if provided).
        """

        order_remove_count = 0
        order_price = current_price

        order_list = self.trade_history[asset].get(type)
        if order_list is not None:
            for order_id in order_list.copy():
                order_cancel = False

                rival_bid = self.asset_price_calculator(rival_price)
                order_status = self.trade_history[asset][type][order_id]["status"]

                # below prices are in float
                order_price = self.trade_history[asset][type][order_id]["price"]

                if float(current_price) == order_price:
                    order_price = current_price

                elif (float(current_price) > order_price) and (order_status is False):
                    order_cancel = True
                    order_price = current_price

                elif (
                    (order_price > rival_bid)
                    and (order_status is False)
                    and (buy is True)
                ):
                    order_cancel = True
                    order_price = rival_price

                if order_cancel is True:
                    if self.test:
                        order_remove_count += 1
                        with self.lock:
                            del self.trade_history[asset][type][order_id]

                        if completed_orders:
                            completed_orders[order_id] = {
                                'status': True, 'price': order_price}
                    else:
                        order_info = self.order.process_order(
                            process_type="query_order", data={"order_id": order_id}
                        )
                        if order_info[0] == 200:
                            if (
                                order_info[1]["status"] != "done"
                                and float(order_info[1]["executedQty"]) == 0
                            ):
                                response = self.order.process_order(
                                    process_type="cancel_order",
                                    data={"symbol": asset,
                                          "order_id": order_id},
                                )

                                if response[0] == 200:
                                    order_remove_count += 1

                                    with self.lock:
                                        del self.trade_history[asset][type][order_id]
                                    if completed_orders:
                                        completed_orders[order_id] = {
                                            "status": True,
                                            "price": order_price,
                                        }

        if completed_orders is None:
            return order_remove_count, str(order_price)
        return order_remove_count, str(order_price), completed_orders

    def buy_asset(self, asset, buy_price, rival_buy_price):
        """_summary_
        Buys an asset at a given buy price, considering rival buy price and trade limits.

        Args:
            asset (str): The symbol or identifier of the asset to be bought.
            buy_price (float): The desired buy price for the asset.
            rival_buy_price (float): The rival buy price to consider.

        Returns: None
        """
        self.check_status(type="sell")
        previous_state, current_state = self.remove_completed_orders(
            asset=asset, type="sell"
        )

        completed_sell_count = len(previous_state) - len(current_state)

        if self.trade_history[asset]["meta"]["sell_count"] != 0:
            self.trade_history[asset]["meta"]["sell_count"] -= completed_sell_count

        (
            remove_count,
            order_price,
        ) = self.check_rival_orders(
            asset=asset,
            type="buy",
            current_price=buy_price,
            rival_price=rival_buy_price,
        )

        self.trade_history[asset]["meta"]["buy_count"] -= remove_count

        trade_limit = self.asset_list[asset]["trade_limit"]
        trade_quantity = self.asset_list[asset]["quantity"]

        if (
            self.trade_history[asset]["meta"]["buy_count"]
            + self.trade_history[asset]["meta"]["sell_count"]
        ) < trade_limit:
            data = {
                "symbol": asset,
                "side": "buy",
                "order_type": "limit",
                "quantity": trade_quantity,
                "price": order_price,
                "stop_price": order_price,
            }

            if self.test:
                self.trade_history[asset]["meta"]["buy_count"] += 1
                self.order_id += 1
                self.trade_history[asset]["buy"][self.order_id] = {"status": False,
                                                                   "price": float(order_price)}
            else:
                response = self.order.process_order(
                    process_type="new_order", data=data)

                if response[0] == 201 or response[0] == 200:
                    self.trade_history[asset]["meta"]["buy_count"] += 1

                    self.trade_history[asset]["buy"][response[1]["id"]] = {
                        "status": False,
                        "price": float(response[1]["price"]),
                    }

    def sell_asset(self, asset, sell_price, rival_sell_price):
        """_summary_
        Buys an asset at a given sell price, considering rival sell price and trade limits.

        Args:
            asset (str): The symbol or identifier of the asset to be bought.
            sel;_price (float): The desired sell price for the asset.
            rival_sell_price (float): The rival sell price to consider.

        Returns: None
        """
        def _price_computation(current_price, completed_orders):
            """_summary_
            Adjusts the prices of completed orders based on the current price.

            Args:
                current_price (float): The current price of the asset.
                completed_orders (dict): A dictionary containing the details of completed orders.

            Returns:
                dict: The updated completed orders with adjusted prices.
            """
            for order_id in completed_orders.copy():
                order_price = completed_orders[order_id]["price"]
                if current_price >= order_price:
                    completed_orders[order_id]["price"] = str(current_price)
                else:
                    order_price = order_price + 0.02 * order_price
                    completed_orders[order_id]["price"] = str(order_price)

            return completed_orders

        def _filter_completed_orders(previous_state, current_state):
            """_summary_
            Filters the completed orders from the previous and current state of orders.

            Args:
                previous_state (dict): A dictionary representing the previous state of orders.
                current_state (dict): A dictionary representing the current state of orders.

            Returns:
                dict: The completed orders from the previous and current state.
            """
            completed_orders = {}
            difference = set(previous_state.keys()).symmetric_difference(
                set(current_state.keys())
            )
            for id in difference:
                completed_orders[id] = previous_state.get(id)
            return completed_orders

        self.check_status(type="buy")
        previous_state, current_state = self.remove_completed_orders(
            asset=asset, type="buy"
        )

        completed_buy_count = len(previous_state) - len(current_state)
        if self.trade_history[asset]["meta"]["buy_count"] != 0:
            self.trade_history[asset]["meta"]["buy_count"] -= completed_buy_count

        remove_count, order_price, completed_orders = self.check_rival_orders(
            asset=asset,
            type="sell",
            current_price=sell_price,
            rival_price=rival_sell_price,
            buy=False,
            completed_orders=_filter_completed_orders(
                previous_state, current_state),
        )

        completed_buy_count += remove_count

        trade_quantity = self.asset_list[asset]["quantity"]
        completed_orders = _price_computation(
            float(order_price), completed_orders)
        for order_id in completed_orders:
            data = {
                "symbol": asset,
                "side": "sell",
                "order_type": "limit",
                "quantity": trade_quantity,
                "price": completed_orders[order_id]["price"],
                "stop_price": completed_orders[order_id]["price"],
            }

            if self.test:
                self.trade_history[asset]["meta"]["sell_count"] += 1
                self.order_id += 1
                self.trade_history[asset]["sell"][self.order_id] = {"status": False,
                                                                    "price": float(order_price)}
            else:
                response = self.order.process_order(
                    process_type="new_order", data=data)

                if response[0] == 201 or response[0] == 200:
                    self.trade_history[asset]["meta"]["sell_count"] += 1
                    self.trade_history[asset]["sell"][response[1]["id"]] = {
                        "status": False,
                        "price": float(response[1]["price"]),
                    }

    def check_status(self, type):
        """_summary_
        Checks the status of open orders of a given type (buy or sell) for all assets in the asset list.
        Updates the status of the orders that have been filled in the trade history.

        Args:
            type (str): Type of order to check status for (either "buy" or "sell").

        Returns:
            None
        """
        for symbol in self.trade_history:
            order_list = self.trade_history[symbol][type]

            for order_id in order_list:
                if self.test:
                    self.trade_history[symbol][type][order_id]["status"] = True
                else:
                    order_info = self.order.process_order(
                        process_type="query_order", data={"order_id": order_id}
                    )

                    if order_info[0] == 200:
                        if order_info[1]["status"] == "done":
                            with self.lock:
                                self.trade_history[symbol][type][order_id]["status"] = True

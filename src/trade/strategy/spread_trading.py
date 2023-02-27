import threading
from time import sleep
from trade.database import DataBase
from trade.market_data import MarketData
from trade.order import Order


class SpreadTrading:
    def __init__(self, api_key=None, api_secret=None, db_url=None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.db_url = db_url

        self.market_data = MarketData(self.api_key, self.api_secret)
        self.order = Order(self.api_key, self.api_secret)
        self.db = DataBase(self.db_url)
        self.asset_list = {}
        self.trade_history = {}
        self.lock = threading.Lock()

        # self.order_id = 0

        self.retrieve_assets()

    def retrieve_assets(self):
        # retrieving data from database
        self.asset_list = self.db.query(
            db_name="wazirx", table_name="asset")["data"]

        # initiate trade history
        self.init_trade_history()

    def init_trade_history(self):
        for asset in self.asset_list:
            if asset not in self.trade_history:
                self.trade_history[asset] = {
                    "buy": {},
                    "sell": {},
                    "meta": {"buy_count": 0, "sell_count": 0},
                }

    def asset_price_calculator(self, asset_price):
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
            except Exception as e:
                print(e)
                # pass

    def remove_completed_orders(self, asset, type=None):
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
                    # #for testing only
                    # order_remove_count += 1
                    # with self.lock:
                    #   del self.trade_history[asset][type][order_id]

                    # if completed_orders:
                    #   completed_orders[order_id] = {'status': True, 'price': order_price}

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
                                data={"symbol": asset, "order_id": order_id},
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

            # # for testing only
            # self.trade_history[asset]["meta"]["buy_count"] += 1
            # self.order_id += 1
            # self.trade_history[asset]["buy"][self.order_id] = {"status": False,
            #                                                    "price": float(order_price)}

            response = self.order.process_order(
                process_type="new_order", data=data)

            if response[0] == 201 or response[0] == 200:
                self.trade_history[asset]["meta"]["buy_count"] += 1

                self.trade_history[asset]["buy"][response[1]["id"]] = {
                    "status": False,
                    "price": float(response[1]["price"]),
                }

    def sell_asset(self, asset, sell_price, rival_sell_price):
        def _price_computation(current_price, completed_orders):
            for order_id in completed_orders.copy():
                order_price = completed_orders[order_id]["price"]
                if current_price >= order_price:
                    completed_orders[order_id]["price"] = str(current_price)
                else:
                    order_price = order_price + 0.02 * order_price
                    completed_orders[order_id]["price"] = str(order_price)

            return completed_orders

        def _filter_completed_orders(previous_state, current_state):
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

            # # for testing only
            # self.trade_history[asset]["meta"]["sell_count"] += 1
            # self.order_id += 1
            # self.trade_history[asset]["sell"][self.order_id] = {"status": False,
            #                                                     "price": float(order_price)}

            response = self.order.process_order(
                process_type="new_order", data=data)

            if response[0] == 201 or response[0] == 200:
                self.trade_history[asset]["meta"]["sell_count"] += 1
                self.trade_history[asset]["sell"][response[1]["id"]] = {
                    "status": False,
                    "price": float(response[1]["price"]),
                }

    def check_status(self, type):
        for symbol in self.trade_history:
            order_list = self.trade_history[symbol][type]

            for order_id in order_list:
                # # for testing only
                # self.trade_history[symbol][type][order_id]["status"] = True

                order_info = self.order.process_order(
                    process_type="query_order", data={"order_id": order_id}
                )

                if order_info[0] == 200:
                    if order_info[1]["status"] == "done":
                        with self.lock:
                            self.trade_history[symbol][type][order_id]["status"] = True

from datetime import datetime
import traceback
from .log import setup_logger
from wazirx.rest.client import Client

from .exception import MissingAttributeError


class Order:
    def __init__(self, api_key=None, api_secret=None):
        """_summary_

        Args:
            api_key (str): wazirx api key
            api_secret (str): wazirx secret key
        Returns:
            self.client: obj instance
            self.recvWindow (int): WazirX has a predetermined value that must be received for an order to be processed. If the order time falls below this value, it will not be processed.
        """
        if not api_key:
            raise MissingAttributeError("api_key required")
        if not api_secret:
            raise MissingAttributeError("api_secret required")

        self.client = Client(api_key=api_key, secret_key=api_secret)
        self.recvWindow = 2000
        self.log = setup_logger()

    def validate(
        self,
        new_order=False,
        symbol=None,
        side=None,
        order_type=None,
        quantity=None,
        price=None,
        stop_price=None,
        query_order=False,
        order_id=None,
        cancel_order=False,
        process_order=False,
        process_type=None,
        data=None,
    ):
        """_summary_

        Acts as middleware (serializer)
        accepts multiple arguments and raise MissingAttributeError & TypeError if missing/invalid
        """
        if new_order:
            if not symbol:
                raise MissingAttributeError("symbol required")
            else:
                if not isinstance(symbol, str):
                    raise TypeError(
                        f"Expected a str for 'symbol' but received a {type(symbol).__name__}."
                    )

            if not side:
                raise MissingAttributeError("side required")
            else:
                if not isinstance(side, str):
                    raise TypeError(
                        f"Expected a str for 'side' but received a {type(side).__name__}."
                    )

            if not order_type:
                raise MissingAttributeError("order_type required")
            else:
                if not isinstance(order_type, str):
                    raise TypeError(
                        f"Expected a str for 'order_type' but received a {type(order_type).__name__}."
                    )

            if not quantity:
                raise MissingAttributeError("quantity required")
            else:
                if not isinstance(quantity, float):
                    raise TypeError(
                        f"Expected a float for 'quantity' but received a {type(quantity).__name__}."
                    )

            if not price:
                raise MissingAttributeError("price required")
            else:
                if not isinstance(price, str):
                    raise TypeError(
                        f"Expected a str for 'price' but received a {type(price).__name__}."
                    )

            if not stop_price:
                raise MissingAttributeError("stop_price required")
            else:
                if not isinstance(stop_price, str):
                    raise TypeError(
                        f"Expected a str for 'stop_price' but received a {type(stop_price).__name__}."
                    )

        elif query_order:
            if not order_id:
                raise MissingAttributeError("order_id required")
            else:
                if not isinstance(order_id, int):
                    raise TypeError(
                        f"Expected a int for 'order_id' but received a {type(order_id).__name__}."
                    )

        elif cancel_order:
            if not symbol:
                raise MissingAttributeError("symbol required")
            else:
                if not isinstance(symbol, str):
                    raise TypeError(
                        f"Expected a str for 'symbol' but received a {type(symbol).__name__}."
                    )

            if not order_id:
                raise MissingAttributeError("order_id required")
            else:
                if not isinstance(order_id, int):
                    raise TypeError(
                        f"Expected a int for 'order_id' but received a {type(order_id).__name__}."
                    )

        elif process_order:
            if not process_type:
                raise MissingAttributeError("process_type required")
            else:
                if not isinstance(process_type, str):
                    raise TypeError(
                        f"Expected a str for 'process_type' but received a {type(process_type).__name__}."
                    )

            if not data:
                raise MissingAttributeError("data required")
            else:
                if not isinstance(data, dict):
                    raise TypeError(
                        f"Expected a dict for 'data' but received a {type(data).__name__}."
                    )

    def test_order(
        self,
        symbol=None,
        side=None,
        order_type=None,
        quantity=None,
        price=None,
        stop_price=None,
    ):
        """_summary_
        Test new order creation and signature/recvWindow long. Validates a new order but does not send it into the matching engine.

        Rate limit: 2 per second
        Args:
            symbol: crypto name
            side: buy/sell side
            order_type: limit/stop_limit
            quantity: order quantity
            price: order price
            stop_price: if any
        Returns:
            response (tuple): (status code, {})
        """
        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send(
            "create_test_order",
            {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price,
                "stopPrice": stop_price,
                "recvWindow": self.recvWindow,
                "timestamp": ts,
            },
        )

    def new_order(
        self,
        symbol=None,
        side=None,
        order_type=None,
        quantity=None,
        price=None,
        stop_price=None,
    ):
        """_summary_
        Send in a new order.

        Rate limit: 10 per second
        Args:
            symbol: crypto name
            side: buy/sell side
            order_type: limit/stop_limit
            quantity: order quantity
            price: order price
            stop_price: if any
        Returns:
            response (tuple): (status code, {})
        """
        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send(
            "create_order",
            {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price,
                "stopPrice": stop_price,
                "recvWindow": self.recvWindow,
                "timestamp": ts,
            },
        )

    def query_order(self, order_id=None):
        """_summary_
        Check an order's status.

        Order status (status):
            idle - The order is idle not yet triggered.
            wait - The order is still open and waiting to be filled completely.
            done - The order has been completely filled.
            cancel - The order has been canceled by the user.

        Rate limit: 2 per second
        Args:
            order_id: unique order id
        Returns:
            response (tuple): (status code, {})
        """
        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send(
            "query_order",
            {"orderId": order_id, "recvWindow": self.recvWindow, "timestamp": ts},
        )

    def cancel_order(self, symbol=None, order_id=None):
        """_summary_
        Cancel an active order.

        Rate limit: 10 per second
        Args:
            symbol: crypto name
            order_id: unique order id
        Returns:
            response (tuple): (status code, {})
        """
        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send(
            "cancel_order",
            {
                "symbol": symbol,
                "orderId": order_id,
                "recvWindow": self.recvWindow,
                "timestamp": ts,
            },
        )

    def process_order(self, process_type=None, data=None):
        """_summary_

        Args:
            process_type (str): type of process to be executed
            data (dict): contains order related details

        Returns:
            response (tuple): order response
        """
        self.validate(process_order=True, process_type=process_type, data=data)

        if process_type == "test_order":
            self.validate(
                new_order=True,
                symbol=data.get("symbol"),
                side=data.get("side"),
                order_type=data.get("order_type"),
                quantity=data.get("quantity"),
                price=data.get("price"),
                stop_price=data.get("stop_price"),
            )
            try:
                return self.test_order(
                    symbol=data.get("symbol"),
                    side=data.get("side"),
                    order_type=data.get("order_type"),
                    quantity=data.get("quantity"),
                    price=data.get("price"),
                    stop_price=data.get("stop_price"),
                )
            except Exception:
                self.log.critical(traceback.format_exc())
                return (404, {"error": "unable to create test order"})

        elif process_type == "new_order":
            self.validate(
                new_order=True,
                symbol=data.get("symbol"),
                side=data.get("side"),
                order_type=data.get("order_type"),
                quantity=data.get("quantity"),
                price=data.get("price"),
                stop_price=data.get("stop_price"),
            )
            try:
                return self.new_order(
                    symbol=data.get("symbol"),
                    side=data.get("side"),
                    order_type=data.get("order_type"),
                    quantity=data.get("quantity"),
                    price=data.get("price"),
                    stop_price=data.get("stop_price"),
                )
            except Exception:
                self.log.critical(traceback.format_exc())
                return (404, {"error": "unable to create order"})

        elif process_type == "query_order":
            self.validate(query_order=True, order_id=data.get("order_id"))

            try:
                return self.query_order(order_id=data.get("order_id"))
            except Exception:
                self.log.critical(traceback.format_exc())
                return (404, {"error": "order doesn't exists"})

        elif process_type == "cancel_order":
            self.validate(
                cancel_order=True,
                symbol=data.get("symbol"),
                order_id=data.get("order_id"),
            )
            try:
                return self.cancel_order(
                    symbol=data.get("symbol"), order_id=data.get("order_id")
                )
            except Exception:
                self.log.critical(traceback.format_exc())
                return (404, {"error": "unable to cancel order"})

        else:
            return (404, {"error": "invalid process type"})

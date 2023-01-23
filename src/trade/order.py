from datetime import datetime

from wazirx.rest.client import Client

from .exception import MissingAttributeError


class Order:
    def __init__(self, api_key=None, api_secret=None):
        if not api_key:
            raise MissingAttributeError("api_key required")
        if not api_secret:
            raise MissingAttributeError("api_secret required")

        self.client = Client(api_key=api_key, secret_key=api_secret)
        self.recvWindow = 2000

    def test_order(self, symbol=None, side=None, order_type=None,
                   quantity=None, price=None, stop_price=None):
        if not symbol:
            raise MissingAttributeError("symbol required")
        if not side:
            raise MissingAttributeError("side required")
        if not order_type:
            raise MissingAttributeError("order_type required")
        if not quantity:
            raise MissingAttributeError("quantity required")
        if not price:
            raise MissingAttributeError("price required")
        if not stop_price:
            raise MissingAttributeError("stop_price required")

        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("create_test_order",
                                {"symbol": symbol,
                                 "side": side,
                                 "type": order_type,
                                 "quantity": quantity,
                                 "price": price,
                                 "stopPrice": stop_price,
                                 "recvWindow": self.recvWindow,
                                 "timestamp": ts})

    def new_order(self, symbol=None, side=None, order_type=None,
                  quantity=None, price=None, stop_price=None):
        if not symbol:
            raise MissingAttributeError("symbol required")
        if not side:
            raise MissingAttributeError("side required")
        if not order_type:
            raise MissingAttributeError("order_type required")
        if not quantity:
            raise MissingAttributeError("quantity required")
        if not price:
            raise MissingAttributeError("price required")
        if not stop_price:
            raise MissingAttributeError("stop_price required")

        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("create_order", {"symbol": symbol,
                                                 "side": side,
                                                 "type": order_type,
                                                 "quantity": quantity,
                                                 "price": price,
                                                 "stopPrice": stop_price,
                                                 "recvWindow": self.recvWindow,
                                                 "timestamp": ts
                                                 })

    def query_order(self, order_id=None):
        if not order_id:
            raise MissingAttributeError("order_id required")

        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("query_order", {"orderId": order_id,
                                                "recvWindow": self.recvWindow,
                                                "timestamp": ts})

    def cancel_order(self, symbol=None, order_id=None):
        if not symbol:
            raise MissingAttributeError("symbol required")
        if not order_id:
            raise MissingAttributeError("order_id required")

        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("cancel_order", {"symbol": symbol,
                                                 "orderId": order_id,
                                                 "recvWindow": self.recvWindow,
                                                 "timestamp": ts})

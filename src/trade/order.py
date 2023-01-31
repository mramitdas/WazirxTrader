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

    def validate(self, new_order=False,
                 symbol=None, side=None, order_type=None,
                 quantity=None, price=None, stop_price=None,
                 query_order=False, order_id=None,
                 cancel_order=False,
                 process_order=False, process_type=None, data=None):
        if new_order:
            if not symbol:
                raise MissingAttributeError("symbol required")
            else:
                if not type(symbol) is str:
                    raise TypeError(
                        f"Expected a str for 'symbol' but received a {type(symbol).__name__}.")

            if not side:
                raise MissingAttributeError("side required")
            else:
                if not type(symbol) is str:
                    raise TypeError(
                        f"Expected a str for 'side' but received a {type(side).__name__}.")

            if not order_type:
                raise MissingAttributeError("order_type required")
            else:
                if not type(symbol) is str:
                    raise TypeError(
                        f"Expected a str for 'order_type' but received a {type(order_type).__name__}.")

            if not quantity:
                raise MissingAttributeError("quantity required")
            else:
                if not type(quantity) is float:
                    raise TypeError(
                        f"Expected a float for 'quantity' but received a {type(quantity).__name__}.")

            if not price:
                raise MissingAttributeError("price required")
            else:
                if not type(symbol) is float:
                    raise TypeError(
                        f"Expected a float for 'price' but received a {type(price).__name__}.")

            if not stop_price:
                raise MissingAttributeError("stop_price required")
            else:
                if not type(stop_price) is float:
                    raise TypeError(
                        f"Expected a float for 'stop_price' but received a {type(stop_price).__name__}.")

        elif query_order:
            if not order_id:
                raise MissingAttributeError("order_id required")
            else:
                if not type(order_id) is str:
                    raise TypeError(
                        f"Expected a str for 'order_id' but received a {type(order_id).__name__}.")

        elif cancel_order:
            if not symbol:
                raise MissingAttributeError("symbol required")
            else:
                if not type(symbol) is str:
                    raise TypeError(
                        f"Expected a str for 'symbol' but received a {type(symbol).__name__}.")

            if not order_id:
                raise MissingAttributeError("order_id required")
            else:
                if not type(order_id) is str:
                    raise TypeError(
                        f"Expected a str for 'order_id' but received a {type(order_id).__name__}.")

        elif process_order:
            if not process_type:
                raise MissingAttributeError("process_type required")
            else:
                if not type(process_type) is str:
                    raise TypeError(
                        f"Expected a str for 'process_type' but received a {type(process_type).__name__}.")

            if not data:
                raise MissingAttributeError("data required")
            else:
                if not type(data) is dict:
                    raise TypeError(
                        f"Expected a dict for 'data' but received a {type(data).__name__}.")

    def test_order(self, symbol=None, side=None, order_type=None,
                   quantity=None, price=None, stop_price=None):

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

        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("query_order", {"orderId": order_id,
                                                "recvWindow": self.recvWindow,
                                                "timestamp": ts})

    def cancel_order(self, symbol=None, order_id=None):

        ct = datetime.now().timestamp()
        ts = int(ct * 1000)
        return self.client.send("cancel_order", {"symbol": symbol,
                                                 "orderId": order_id,
                                                 "recvWindow": self.recvWindow,
                                                 "timestamp": ts})

    def process_order(self, process_type=None, data=None):

        self.validate(process_order=True)

        if process_type == "test_order":
            self.validate(new_order=True, symbol=data.get("symbol"),
                          side=data.get("side"), order_type=data.get("order_type"),
                          quantity=data.get("quantity"), price=data.get("price"),
                          stop_price=data.get("stop_price"))

            self.test_order(symbol=data.get("symbol"),
                            side=data.get("side"), order_type=data.get("order_type"),
                            quantity=data.get("quantity"), price=data.get("price"),
                            stop_price=data.get("stop_price"))

        elif process_type == "new_order":
            self.validate(new_order=True, symbol=data.get("symbol"),
                          side=data.get("side"), order_type=data.get("order_type"),
                          quantity=data.get("quantity"), price=data.get("price"),
                          stop_price=data.get("stop_price"))

            self.new_order(symbol=data.get("symbol"),
                           side=data.get("side"), order_type=data.get("order_type"),
                           quantity=data.get("quantity"), price=data.get("price"),
                           stop_price=data.get("stop_price"))

        elif process_type == "query_order":
            self.validate(query_order=True, order_id=data.get("order_id"))

            self.query_order(order_id=data.get("order_id"))

        elif process_type == "cancel_order":
            self.validate(cancel_order=True, symbol=data.get(
                "symbol"), order_id=data.get("order_id"))

            self.cancel_order(symbol=data.get(
                "symbol"), order_id=data.get("order_id"))

        else:
            return {"error": "invalid process type"}

from .exception import MissingAttributeError


class Quantity:
    def __init__(self, base_amount=None, asset={}, share_percent=30):
        if not base_amount:
            raise MissingAttributeError("base_amount required")
        if asset == {}:
            raise MissingAttributeError("asset dict required")

        self.base_amount = base_amount
        self.asset = asset
        self.share_percent = share_percent

    def amount_calculator(self):
        return int(self.base_amount / len(self.asset))

    def quantity_calculator(self):
        funds_issued = self.amount_calculator()

        for symbol in self.asset:
            self.asset[symbol]["quantity"] = round(
                ((funds_issued / self.asset[symbol]["buy"]) * (self.share_percent / 100)), 1)

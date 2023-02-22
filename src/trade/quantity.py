from .exception import MissingAttributeError


class Quantity:
    def __init__(self, base_amount=None, asset=None, share_percent=None):
        """_summary_

        Args:
            base_amount (int): overall amount allocated by user
            asset (dict): pre-processed symbols
            share_percent (int): percentage of share user like to buy/sell at a time between 0-100
        Returns:
            self.asset: processed symbols after quantity calculation
        """
        self.base_amount = base_amount
        self.asset = asset
        self.share_percent = share_percent

        self.validate(
            base_amount=self.base_amount,
            asset=self.asset,
            share_percent=self.share_percent,
        )
        self.quantity_calculator()

    def validate(self, base_amount=None, asset=None, share_percent=None):
        """_summary_

        Acts as middleware (serializer)
        accepts multiple arguments and raise MissingAttributeError & TypeError if missing/invalid
        """
        if not base_amount:
            raise MissingAttributeError("base_amount required")
        else:
            if not isinstance(base_amount, int):
                raise TypeError(
                    f"Expected a int for 'base_amount' but received a {type(base_amount).__name__}."
                )

        if asset is None:
            raise MissingAttributeError("asset dict required")
        else:
            if not isinstance(asset, dict):
                raise TypeError(
                    f"Expected a dict for 'asset' but received a {type(asset).__name__}."
                )

        if not share_percent:
            raise MissingAttributeError("share_percent required")
        else:
            if not isinstance(share_percent, int):
                raise TypeError(
                    f"Expected a int for 'share_percent' but received a {type(share_percent).__name__}."
                )

    def amount_calculator(self):
        """_summary_

        calculates the amount to be allocated for each crypto

        Args: NONE
        Returns:
            int: amount allocated for each crypto
        """
        return int(self.base_amount / len(self.asset))

    def quantity_calculator(self):
        """_summary_

        calculates the quantity to be purchased for each crypto
        condition -> min cost to be purchased should be greater than 60 (wazrix limitation)

        Args: NONE
        Returns:
            int: amount allocated for each crypto
        """
        if self.asset != {}:
            try:
                funds_issued = self.amount_calculator()

                for symbol in self.asset:
                    symbol_quantity = round(
                        (
                            (funds_issued / self.asset[symbol]["buy"])
                            * (self.share_percent / 100)
                        ),
                        1,
                    )

                    if (symbol_quantity * self.asset[symbol]["buy"]) > 60:
                        self.asset[symbol]["quantity"] = symbol_quantity
                    else:
                        symbol_quantity = round(
                            60 / self.asset[symbol]["buy"], 1)
                        self.asset[symbol]["quantity"] = symbol_quantity

                    self.asset[symbol]["trade_limit"] = int(
                        funds_issued / (symbol_quantity *
                                        self.asset[symbol]["buy"])
                    )

            except Exception as e:
                pass

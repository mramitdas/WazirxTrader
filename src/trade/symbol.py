from .base import Base


class Symbol:
    def __init__(self):
        """_summary_

        Args: NONE
        Returns:
            symbol_list:  A list of symbols with INR as the quote asset.
        """
        self.symbol_list = self.get_updated_symbol_list()

    def get_updated_symbol_list(self):
        """_summary_
        Get an updated list of symbols from WazirX.

        Args: NONE
        Returns:
            symbol_list:  A list of symbols with INR as the quote asset.
        """
        data = Base().exchange_info()
        symbol_list = [x['symbol']
                       for x in data[1]['symbols'] if x.get('quoteAsset') == 'inr']
        return symbol_list

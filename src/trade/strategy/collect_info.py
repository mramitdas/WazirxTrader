from trade.quantity import Quantity
from trade.market_data import MarketData
from trade.database import DataBase


class CollectInfo:
    def __init__(self, api_key=None, api_secret=None, db_url=None,
                 symbols=None, apply_filter=False,
                 amount_limit=None, symbol_limit=None, depth_limit=None,
                 base_amount=None, share_percent=33):

        self.api_key = api_key
        self.api_secret = api_secret
        self.db_url = db_url

        self.symbols = symbols
        self.amount_limit = amount_limit
        self.symbol_limit = symbol_limit
        self.depth_limit = depth_limit
        self.apply_filter = apply_filter
        self.base_amount = base_amount
        self.share_percent = share_percent

        self.market_data = MarketData(self.api_key, self.api_secret)
        self.db = DataBase(self.db_url)
        self.asset_list = {}

        self.collect_info()
        self.dump_assets()

    def collect_info(self):
        # get market data
        self.market_data.process_symbol(self.symbols, self.apply_filter,
                                        self.amount_limit, self.symbol_limit, self.depth_limit)

        self.asset_list = self.market_data.filtered_asset

        # data filtration & sorting
        quantity = Quantity(self.base_amount, asset=self.asset_list,
                            share_percent=self.share_percent)
        self.asset_list = quantity.asset

    def dump_assets(self):
        # removing old data from database
        old_assets = self.db.query(
            db_name="wazirx", table_name="asset", bulk=True)

        for asset in old_assets:
            self.db.delete(db_name="wazirx", table_name="asset",
                           filter={"_id": asset["_id"]})

        # dumping new data into database
        self.db.upload(db_name="wazirx", table_name="asset",
                       data={"data": self.asset_list})

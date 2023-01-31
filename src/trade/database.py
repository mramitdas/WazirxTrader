from datetime import datetime

import pymongo
import pytz

from .exception import MissingAttributeError


class DataBase:
    """
    This is a common database class which is called in every function

    Working: Database instance can be created by calling DataBase class along with the required arguments.

    Attributes:
        db_url -- Database url
        db_name -- Database name
        table_name -- Database table name

    Returns:
        database -- refers to specific database which might contain several tables.
        dataset -- refers to specific table present in database.
        storage -- refers to storage container which contains data like image, pdf,..,etc.
    """

    def __init__(self, db_url=None):
        if not db_url:
            raise MissingAttributeError("db_url required")
        else:
            if not type(db_url) is str:
                raise TypeError(
                    f"Expected a str for 'db_url' but received a {type(db_url).__name__}.")

        self.database_url = db_url
        self.mongod = self.connect()

    def connect(self):
        return pymongo.MongoClient(self.database_url)

    def validate(self, db_name=None, table_name=None,
                 data_opt=False, data=None,
                 filter_opt=False, filter=None,
                 bulk=False):
        if not db_name:
            raise MissingAttributeError("db_name required")
        else:
            if not type(db_name) is str:
                raise TypeError(
                    f"Expected a str for 'db_name' but received a {type(db_name).__name__}.")

        if not table_name:
            raise MissingAttributeError("table_name required")
        else:
            if not type(table_name) is str:
                raise TypeError(
                    f"Expected a str for 'table_name' but received a {type(table_name).__name__}.")

        if data_opt:
            if not data:
                raise MissingAttributeError("data required")
            else:
                if not (type(data) is dict or type(data) is list):
                    raise TypeError(
                        f"Expected a dict/list for 'data' but received a {type(data).__name__}.")

        if filter_opt:
            if not filter:
                raise MissingAttributeError("filter required")
            else:
                if not type(filter) is dict:
                    raise TypeError(
                        f"Expected a dict for 'filter' but received a {type(filter).__name__}.")

        if bulk:
            if not type(bulk) is bool:
                raise TypeError(
                    f"Expected a bool for 'bulk' but received a {type(bulk).__name__}.")

    def upload(self, db_name=None, table_name=None, data=None):
        self.validate(db_name, table_name, data_opt=True, data=data)

        # time-zone
        ist = pytz.timezone('Asia/Kolkata')

        database = self.mongod[db_name]
        dataset = database[table_name]

        if type(data) is dict:
            time_stamp = datetime.now(ist).strftime('%Y-%m-%d || %H:%M:%S:%f')
            data["_id"] = time_stamp
            response = dataset.insert_one(data)
        else:
            [x.update(
                {"_id": datetime.now(ist).strftime('%Y-%m-%d || %H:%M:%S:%f')}
            ) for x in data]
            response = dataset.insert_many(data)

        return response

    def query(self, db_name=None, table_name=None, filter=None, bulk=False):
        if filter:
            filter_opt = True
        else:
            filter_opt = False

        self.validate(db_name, table_name,
                      filter_opt=filter_opt, filter=filter, bulk=bulk)

        database = self.mongod[db_name]
        dataset = database[table_name]

        if bulk:
            if filter:
                response = dataset.find(filter)
            else:
                response = dataset.find()
        elif filter:
            response = dataset.find_one(filter)
        else:
            response = dataset.find_one()

        return response

    def update(self, db_name=None, table_name=None, data=None, bulk=False):
        self.validate(db_name, table_name,
                      data_opt=True, data=data,
                      bulk=bulk)

        database = self.mongod[db_name]
        dataset = database[table_name]

        if bulk:
            response = dataset.update_many(data)
        else:
            response = dataset.update_one(data)

        return response

    def delete(self, db_name=None, table_name=None, filter=None):
        self.validate(db_name, table_name, filter_opt=True, filter=filter)

        database = self.mongod[db_name]
        dataset = database[table_name]
        response = dataset.delete_one(filter)

        return response

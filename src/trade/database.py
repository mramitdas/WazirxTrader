import gridfs
import pymongo

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

    def __init__(self, db_url=None, db_name=None, table_name=None):
        self.database_url = db_url
        self.database_name = db_name
        self.table_name = table_name

        self.error_handling()
        self.database, self.dataset, self.storage = self.mongo()

    def mongo(self):
        mongod = pymongo.MongoClient(self.database_url)
        database = mongod[self.database_name]
        dataset = database[self.table_name]
        storage = gridfs.GridFS(database)

        return database, dataset, storage

    def error_handling(self):
        if self.database_url is None:
            raise MissingAttributeError("DataBase URL required.")
        if self.database_name is None:
            raise MissingAttributeError("DataBase Name required.")
        if self.table_name is None:
            raise MissingAttributeError("Table name required.")

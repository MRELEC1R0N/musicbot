from pymongo import MongoClient

class Database:
    def __init__(self, uri, dbname):
        self.client = MongoClient(uri)
        self.db = self.client[dbname]

    def get_collection(self, collection_name):
        return self.db[collection_name]
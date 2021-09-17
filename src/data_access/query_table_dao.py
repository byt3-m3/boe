from utils.pymongo_utils import get_client, get_database, get_collection, add_item
from dataclasses import  dataclass
from uuid import UUID


@dataclass
class Item:
    id: UUID



class QueryTableDAO:
    def __init__(self, db_host, db_port, db_name):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.collection_name = 'QueryTable'
        self.client = get_client(db_host=self.db_host, db_port=self.db_port)
        self.db = get_database(client=self.client, db_name=self.db_name)
        self.collection = get_collection(database=self.db, collection=self.collection_name)


    def add_bank_account(self, **kwargs):
        print(kwargs)

    def add_account(self, _id, **kwargs):
       results = add_item(collection=self.collection, item=kwargs)
       print(results)
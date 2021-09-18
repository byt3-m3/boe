from utils.pymongo_utils import get_client, get_database, get_collection, add_item, query_items
from dataclasses import dataclass
from uuid import UUID
from bson import decode


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

    @staticmethod
    def _convert_cursors(items):
        return [
            decode(item.raw)
            for item in items
        ]

    def add_bank_account(self, **kwargs):
        print(kwargs)

    def add_aggregate(self, _id, **kwargs):
        if "_id" not in kwargs.keys():
            kwargs["_id"] = _id
        return add_item(collection=self.collection, item=kwargs)

    def scan_adult_aggregates(self):
        items = query_items(collection=self.collection, query={"_type": "src.domains.user_domain.AdultAggregate"})
        return self._convert_cursors(items=items)

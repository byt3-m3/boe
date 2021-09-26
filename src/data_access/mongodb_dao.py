from car_finder.data_access.dao import DAOMixinInterface, BaseDAO
from src.utils.pymongo_utils import (
    get_client,
    get_collection,
    get_item,
    update_item,
    add_item,
    get_database,
    query_items,
    delete_item,
    DEFAULT_ITEM_KEY,
    InsertOneResult,
    DeleteResult,
    UpdateResult,
    Cursor,
    get_page_from_collection,
    get_pages_from_collection

)
from car_finder.models.pagination_models import NewPage
from car_finder.utils.pagination_utils import Paginator


class _MongoDBPymongoMixin(DAOMixinInterface):
    def query_items(self, query):
        return query_items(collection=self.collection, query=query)

    def get_item(self, item_id, item_key=DEFAULT_ITEM_KEY) -> Cursor:
        return get_item(collection=self.collection, item_id=item_id, item_key=item_key)

    def update_item(self, item_id, new_values, item_key=DEFAULT_ITEM_KEY) -> UpdateResult:
        return update_item(collection=self.collection, item_id=item_id, new_values=new_values, item_key=item_key)

    def add_item(self, item: dict, key_id='_id') -> InsertOneResult:
        return add_item(collection=self.collection, item=item, key_id=key_id)

    def delete_item(self, item_id, item_key=DEFAULT_ITEM_KEY) -> DeleteResult:
        return delete_item(collection=self.collection, item_id=item_id, item_key=item_key)

    def scan_items(self):
        return query_items(collection=self.collection, query={})

    def get_page(self, query, limit_per_page=500, last_item_id=None) -> NewPage:
        return get_page_from_collection(self.collection, query=query, limit=limit_per_page, last_item_id=last_item_id)

    def get_pages(self, query, limit_per_page=500) -> Paginator:
        return get_pages_from_collection(self.collection, query=query, limit=limit_per_page)


class MongoDBDAO(BaseDAO, _MongoDBPymongoMixin):
    def __init__(self, host, port, db, collection):
        self._host = host
        self._port = port

        self._client = get_client(db_host=self._host, db_port=self._port)

        self.db = db
        self.collection = collection

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, collection):
        self._collection = get_collection(self._db, collection)

    @property
    def db(self):
        return self._db

    @db.setter
    def db(self, db):
        self._db = get_database(client=self._client, db_name=db)

    @property
    def client(self):
        return self._client

from typing import Union, List
from uuid import UUID

from bson import ObjectId
from bson.codec_options import CodecOptions, UuidRepresentation
from bson.raw_bson import RawBSONDocument
from eventsourcing.persistence import Mapper, DomainEvent, StoredEvent
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, BulkWriteError
from pymongo.results import DeleteResult, UpdateResult, InsertOneResult, InsertManyResult
from src.utils.core_utils import clone_item
from src.utils.paging_utils import Paginator, NewPage, PaginationPage

DEFAULT_ITEM_KEY = "_id"

codec_options = CodecOptions(
    document_class=RawBSONDocument,
    uuid_representation=UuidRepresentation.STANDARD

)


def covert_domain_event(event: DomainEvent) -> StoredEvent:
    return Mapper.from_domain_event(event)


def make_objectid() -> ObjectId:
    return ObjectId()


def get_client(db_host, db_port=27017) -> MongoClient:
    # return MongoClient(host=db_host, port=db_port, uuidRepresentation="standard")
    return MongoClient(host=db_host, port=db_port)


def get_database(client: MongoClient, db_name: str) -> Database:
    return client[db_name]


def get_collection(database: Database, collection: str) -> Collection:
    return database.get_collection(name=collection, codec_options=codec_options)


def query_items(collection: Collection, query: dict) -> Cursor:
    return collection.find(query)


def scan_items(collection: Collection) -> Cursor:
    return collection.find()


def update_item(collection: Collection, item_id: Union[str, int], new_values: dict,
                item_key=DEFAULT_ITEM_KEY) -> UpdateResult:
    return collection.update_one(
        {
            f"{item_key}": item_id
        },
        {
            "$set": new_values
        }
    )


def add_item(collection: Collection, item: dict, key_id='_id') -> InsertOneResult:
    try:
        if not key_id == '_id':
            item['_id'] = item[key_id]

        return collection.insert_one(document=item)

    except DuplicateKeyError:
        raise


def delete_item(collection: Collection, item_id: Union[str, int], item_key=DEFAULT_ITEM_KEY) -> DeleteResult:
    return collection.delete_one(
        {
            f"{item_key}": item_id
        },

    )


def get_item(collection: Collection, item_id: Union[str, int, UUID], item_key=DEFAULT_ITEM_KEY) -> Cursor:
    results = collection.find(
        {
            f"{item_key}": item_id
        }
    )

    return results


def get_page_from_collection(collection: Collection, query: dict, limit, last_item_id=None) -> NewPage:
    total_records = collection.find(query).count()

    if last_item_id:
        query.update({"_id": {"$gt": last_item_id}})

    cursor = collection.find(query).limit(limit)

    last_item_id = _get_last_id_from_cursor(cursor=cursor)

    return NewPage(
        cursor=cursor,
        last_id=last_item_id,
        total_items=total_records
    )


def get_pages_from_collection(collection: Collection, query: dict, limit: int) -> Paginator:
    paginator = Paginator()

    total_records = collection.find(query).count()
    total_pages = round(total_records / limit)
    paginator.total_records = total_records

    for i in range(total_pages):
        i += 1

        _page = get_page_from_collection(collection=collection, query=query, limit=limit)
        paginator.add_page(page=PaginationPage(
            cursor=_page.cursor,
            next_page=i + 1 if i < total_pages else i,
            current_page=i,
            item_count=limit
        ))

    return paginator


def _get_last_id_from_cursor(cursor):
    _cursor = clone_item(cursor)
    cursor_list = list(_cursor)
    try:
        return cursor_list[len(cursor_list) - 1].get("_id")

    except IndexError:
        return None


def _get_cursor_count(cursor):
    _cursor = clone_item(cursor)
    cursor_list = list(_cursor)
    return len(cursor_list)


def add_many_items(collection: Collection, items: List[dict], ordered: bool = True) -> InsertManyResult:
    for item in items:
        item['_id'] = item['originator_id']

    try:

        return collection.insert_many(
            documents=items,
            ordered=ordered
        )

    except BulkWriteError:
        for item in items:
            update_item(collection=collection, item_id=item['_id'], item_key='_id', new_values=item)


def check_for_items(collection: Collection):
    collection.aggregate()

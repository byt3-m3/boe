from dataclasses import dataclass
from typing import List
from uuid import UUID

from bson import decode
from cbaxter1988_utils.src.pymongo_utils import (
    get_client,
    get_database,
    get_collection,
    add_item,
    query_items,
    update_item
)
from src.enums import GenderEnum, PermissionsEnum
from src.models.read_models.user_models import (
    ChildReadModel,
    UserAccountReadModel,
    RoleReadModel
)


@dataclass
class Item:
    id: UUID


def map_child_read_model(item: dict) -> ChildReadModel:
    return ChildReadModel.encode(item)


def map_role_read_model(item: dict) -> RoleReadModel:
    return RoleReadModel.encode(item)


def map_user_account_read_model(item: dict) -> UserAccountReadModel:
    return UserAccountReadModel.encode(item)


conversion_map = {
    "gender": {
        "encode_type": GenderEnum,
        "decode_type": int,
        "encode": lambda x: GenderEnum(x),
        "decode": lambda x: x.value
    },
    "permissions": {
        "encode_type": PermissionsEnum,
        "decode_type": int,
        "encode": lambda x: PermissionsEnum(x),
        "decode": lambda x: x.value
    }

}


def endcode_items(items: List[dict]):
    for data in items:
        new_data = {}
        for key, val in data.items():

            if key in conversion_map.keys():
                encode_type = conversion_map[key]['encode_type']
                if not isinstance(val, encode_type):
                    if isinstance(val, list):
                        new_vals = []
                        for v in val:
                            new_vals.append(conversion_map[key]['encode'](v))

                        data[key] = new_vals
                else:
                    val = conversion_map[key]['encode'](val)
                    data[key] = val

    return items


def decode_items(items: List[dict]):
    for data in items:
        new_data = {}
        for key, val in data.items():
            if key in conversion_map.keys():
                decode_type = conversion_map[key]['decode_type']
                if not isinstance(val, decode_type):
                    if isinstance(val, list):
                        new_vals = []
                        for v in val:
                            new_vals.append(conversion_map[key]['decode'](v))

                        data[key] = new_vals
                    else:
                        val = conversion_map[key]['decode'](val)
                        data[key] = val

    return items


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

    def add_aggregate(self, _id, collection=None, **kwargs):
        if "_id" not in kwargs.keys():
            kwargs["_id"] = _id

        _collection = self.collection
        if collection:
            _collection = get_collection(self.db, collection=collection)

        return add_item(collection=_collection, item=kwargs)

    def update_aggregate(self, _id, collection=None, **kwargs):

        _collection = self.collection
        if collection:
            _collection = get_collection(self.db, collection=collection)

        return update_item(
            collection=_collection,
            item_key="_id",
            item_id=_id,
            new_values=kwargs
        )

    def scan_adult_aggregates(self) -> List[UserAccountReadModel]:
        data = self._convert_cursors(
            items=query_items(collection=self.collection, query={"_type": "src.domains.user_domain.AdultAggregate"})
        )

        return list(map(map_user_account_read_model, data))

    def scan_child_aggregates(self) -> List[ChildReadModel]:
        data = self._convert_cursors(
            items=query_items(collection=self.collection, query={"_type": "src.domains.user_domain.ChildAggregate"})
        )

        return list(map(map_child_read_model, data))

    def scan_role_aggregates(self) -> List[RoleReadModel]:
        data = self._convert_cursors(
            items=query_items(collection=self.collection, query={"_type": "src.domains.user_domain.RoleAggregate"})
        )
        return (list(map(map_role_read_model, data)))

    def query(self, query: dict, collection: str):
        items = query_items(
            collection=get_collection(database=self.db, collection=collection),
            query=query

        )
        data = self._convert_cursors(items)
        return list(map(map_child_read_model, data))

    def query_child(self, query: dict) -> ChildReadModel:
        items = query_items(
            collection=self.collection,
            query={
                "_type": "src.domains.user_domain.ChildAggregate",
                **query
            }
        )
        data = self._convert_cursors(items)
        return list(map(map_child_read_model, data))

    def query_role(self, query: dict) -> ChildReadModel:
        items = query_items(
            collection=self.collection,
            query={
                "_type": "src.domains.user_domain.RoleAggregate",
                **query
            }
        )
        data = self._convert_cursors(items)
        return list(map(map_role_read_model, data))

from dataclasses import asdict
from typing import List, Any, Optional
from uuid import UUID

from eventsourcing.domain import TAggregate
from eventsourcing.persistence import AggregateRecorder, StoredEvent
from src.enums import PermissionsEnum
from src.utils.pymongo_utils import (
    add_many_items,
    get_client,
    get_collection,
    get_database,
    get_item
)


def verify_aggregate_permission(aggergate: TAggregate, expected_permission: PermissionsEnum) -> bool:
    assert aggergate.permissions
    if expected_permission in aggergate.permissions:
        return True
    else:
        return False


def verify_aggregate_admin(aggergate: TAggregate, expected_admin: TAggregate) -> bool:
    assert aggergate.admin_map
    assert expected_admin.permissions

    if expected_admin.id in aggergate.admin_map:
        return True
    else:
        return False


def verify_aggregate_permissions(aggergate: TAggregate, expected_permissions: List[PermissionsEnum]):
    results = [
        verify_aggregate_permission(aggergate=aggergate, expected_permission=permission)
        for permission in
        expected_permissions
    ]

    if True in results:
        return True
    else:
        return False


class MongoRecorder(AggregateRecorder):

    def __init__(self, db_host, db_port):
        self._client = get_client(db_host=db_host, db_port=db_port)
        self._db = get_database(client=self._client, db_name='AggregateRecorder')
        self.collection = get_collection(database=self._db, collection='aggregate_events')

    def insert_events(self, stored_events: List[StoredEvent], **kwargs: Any) -> None:
        results = add_many_items(
            collection=self.collection,
            items=[asdict(event) for event in stored_events],
            ordered=True
        )

    def select_events(
            self,
            originator_id: UUID,
            gt: Optional[int] = None,
            lte: Optional[int] = None,
            desc: bool = False,
            limit: Optional[int] = None,
    ) -> List[StoredEvent]:
        cursor = get_item(collection=self.collection, item_id=originator_id, item_key='originator_id')

        return [
            StoredEvent(
                originator_id=record['originator_id'],
                topic=record['topic'],
                originator_version=record['originator_version'],
                state=bytes(record['state'])
            ) for record in cursor
        ]

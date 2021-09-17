from dataclasses import asdict
from typing import List, Any, Optional
from uuid import UUID

from eventsourcing.domain import TAggregate
from eventsourcing.persistence import AggregateRecorder, StoredEvent, ApplicationRecorder, Notification
from src.enums import PermissionsEnum
from src.domains.user_domain import RoleAggregate
from src.utils.pymongo_utils import (
    add_many_items,
    get_client,
    get_collection,
    get_database,
    get_item,
    scan_items
)


def verify_role_permissions(roles: List[RoleAggregate], expected_permissions: List[PermissionsEnum]) -> bool:
    def filter_permissions(permission):
        for _role in roles:
            for p in _role.permissions:
                if p == permission:
                    return True
                else:
                    return False

    filtered_permissions = list(filter(filter_permissions, expected_permissions))
    if len(filtered_permissions) > 0:
        return True
    else:
        return False


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


class MongoRecorder(ApplicationRecorder):

    def __init__(self, db_host, db_port):
        self._client = get_client(db_host=db_host, db_port=db_port)
        self._db = get_database(client=self._client, db_name='AggregateRecorder')
        self.collection = get_collection(database=self._db, collection='aggregate_events')

    def insert_events(self, stored_events: List[StoredEvent], **kwargs: Any) -> None:
        results = add_many_items(
            collection=self.collection,
            items=[asdict(event) for event in stored_events],
            ordered=True,

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

        return self._prepare_return(cursor=cursor)

    def scan_events(self):
        cursor = scan_items(collection=self.collection)
        return self._prepare_return(cursor=cursor)

    def get_event_ids(self):
        cursor = scan_items(collection=self.collection)
        stored_events = self._prepare_return(cursor)
        return [
            event.originator_id for event in stored_events
        ]

    @staticmethod
    def _prepare_return(cursor) -> List[StoredEvent]:
        return [
            StoredEvent(
                originator_id=record['originator_id'],
                topic=record['topic'],
                originator_version=record['originator_version'],
                state=record['state']
            ) for record in cursor
        ]

    def select_notifications(self, start: int, limit: int) -> List[Notification]:
        pass

    def max_notification_id(self) -> int:
        pass
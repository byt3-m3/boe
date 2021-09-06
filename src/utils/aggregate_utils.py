from typing import List

from eventsourcing.domain import TAggregate
from src.enums import PermissionsEnum


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

from dataclasses import dataclass
from typing import List

from eventsourcing.domain import Aggregate, event
from src.enums import PermissionsEnum


@dataclass
class Role(Aggregate):
    name: str
    permissions: List[PermissionsEnum]

    @event
    def append_permission(self, permission: PermissionsEnum):
        assert permission not in self.permissions
        self.permissions.append(permission)

    @event
    def remove_permission(self, permission: PermissionsEnum):
        assert permission not in self.permissions
        self.permissions.append(permission)

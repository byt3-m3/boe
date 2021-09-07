from src.domains.core_domain import CoreAggregate
from dataclasses import dataclass, field
from src.models.user_models import (
    FamilyDataModel,
    ChildDataModel,
    AdultDataModel,
    RoleDataModel
)
from eventsourcing.domain import AggregateEvent
from typing import List, Dict
from uuid import UUID
from src.enums import (
    PermissionsEnum

)
from collections import defaultdict

@dataclass
class RoleAggregate(CoreAggregate):
    model: RoleDataModel

    def append_permission(self, permission: PermissionsEnum):
        self.trigger_event(self.AppendPermissionEvent, permission=permission)

    def remove_permission(self, permission: PermissionsEnum):
        self.trigger_event(self.RemovePermissionEvent, permission=permission)

    class AppendPermissionEvent(AggregateEvent):
        permission: PermissionsEnum

        def apply(self, aggregate: 'RoleAggregate') -> None:
            aggregate.model.permissions.append(self.permission)

    class RemovePermissionEvent(AggregateEvent):
        permission: PermissionsEnum

        def apply(self, aggregate: 'RoleAggregate') -> None:
            aggregate.model.permissions.remove(self.permission)


@dataclass
class UserAccountAggregate(CoreAggregate):
    role_mapping: Dict[UUID, RoleAggregate]

    def add_role(self, role: RoleAggregate):
        self.trigger_event(
            self.AddRoleEvent,
            role=role
        )

    def remove_role(self, role: RoleAggregate):
        self.trigger_event(
            self.RemoveRoleEvent,
            role=role
        )

    class AddRoleEvent(AggregateEvent):
        role: RoleAggregate

        def apply(self, aggregate: 'ChildAggregate') -> None:
            aggregate.role_mapping[self.role.id] = self.role

    class RemoveRoleEvent(AggregateEvent):
        role: RoleAggregate

        def apply(self, aggregate: 'ChildAggregate') -> None:
            aggregate.role_mapping.pop(self.role.id)


@dataclass
class ChildAggregate(UserAccountAggregate):
    model: ChildDataModel


@dataclass
class AdultAggregate(UserAccountAggregate):
    model: AdultDataModel


@dataclass
class FamilyAggregate(CoreAggregate):
    model: FamilyDataModel
    children_mapping: Dict[UUID, 'ChildAggregate'] = field(default_factory=dict)
    parent_mapping: Dict[UUID, 'AdultAggregate'] = field(default_factory=dict)

    def add_child(self, child: ChildAggregate):
        self.trigger_event(
            self.AddChildEvent,
            child=child
        )

    def remove_child(self, child: ChildAggregate):
        self.trigger_event(
            self.RemoveChildEvent,
            child=child
        )

    class AddParentEvent(AggregateEvent):
        parent: AdultAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate.parent_mapping[self.parent.id] = self.parent

    class RemoveParentEvent(AggregateEvent):
        parent: AdultAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate.parent_mapping.pop(self.parent.id)

    class AddChildEvent(AggregateEvent):
        child: ChildAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate.children_mapping[self.child.id] = self.child

    class RemoveChildEvent(AggregateEvent):
        child: ChildAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate.children_mapping.pop(self.child.id)

from src.domains.core_domain import CoreAggregate
from dataclasses import dataclass, field
from src.models.user_models import (
    FamilyDataModel,
    UserDataModel,
    ChildDataModel,
    AdultDataModel,
    RoleDataModel
)
from eventsourcing.domain import AggregateEvent, event
from typing import List, Dict
from uuid import UUID
from src.enums import (
    PermissionsEnum

)


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
            if self.permission not in aggregate.model.permissions:
                aggregate.model.permissions.append(self.permission)
            else:
                raise PermissionError(f"{self.permission} Already Present in Permissions")

    class RemovePermissionEvent(AggregateEvent):
        permission: PermissionsEnum

        def apply(self, aggregate: 'RoleAggregate') -> None:
            if self.permission in aggregate.model.permissions:
                aggregate.model.permissions.remove(self.permission)
            else:
                raise PermissionError(f"{self.permission} not in permission list")


@dataclass
class UserAccountAggregate(CoreAggregate):
    model: UserDataModel
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

    @event("ChangeFirstName")
    def change_first_name(self, value):
        self.model.first_name = value

    @event("ChangeLastName")
    def change_first_name(self, value):
        self.model.last_name = value

    @event("ChangeEmail")
    def change_first_name(self, value):
        self.model.email = value

    @event("AddRoleEvent")
    def add_role(self, role: RoleAggregate):
        self.role_mapping[role.id] = role

    @event("RemoveRoleEvent")
    def remove_role(self, role: RoleAggregate):
        self.role_mapping.pop(role.id)


@dataclass
class ChildAggregate(UserAccountAggregate):
    model: ChildDataModel


@dataclass
class AdultAggregate(UserAccountAggregate):
    model: AdultDataModel


@dataclass
class FamilyAggregate(CoreAggregate):
    model: FamilyDataModel
    _children_mapping: Dict[UUID, 'ChildAggregate'] = field(default_factory=dict)
    _parent_mapping: Dict[UUID, 'AdultAggregate'] = field(default_factory=dict)

    def get_child(self, child: ChildAggregate):
        return self._children_mapping.get(child.id)

    def get_parent(self, parent: AdultAggregate):
        return self._parent_mapping.get(parent.id)

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

    def add_parent(self, parent: AdultAggregate):
        self.trigger_event(
            self.AddParentEvent,
            parent=parent
        )

    def remove_parent(self, parent: AdultAggregate):
        self.trigger_event(
            self.RemoveParentEvent,
            parent=parent
        )

    class AddParentEvent(AggregateEvent):
        parent: AdultAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate._parent_mapping[self.parent.id] = self.parent

    class RemoveParentEvent(AggregateEvent):
        parent: AdultAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate._parent_mapping.pop(self.parent.id)

    class AddChildEvent(AggregateEvent):
        child: ChildAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate._children_mapping[self.child.id] = self.child

    class RemoveChildEvent(AggregateEvent):
        child: ChildAggregate

        def apply(self, aggregate: 'FamilyAggregate') -> None:
            aggregate._children_mapping.pop(self.child.id)

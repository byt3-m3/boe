from dataclasses import dataclass, field
from typing import Dict
from uuid import UUID

from eventsourcing.domain import AggregateEvent, event
from src.domains.core_domain import CoreAggregate
from src.enums import (
    PermissionsEnum,
    GenderEnum

)
from src.models.user_models import (
    FamilyDataModel,
    UserDataModel,
    ChildDataModel,
    AdultDataModel,
    RoleDataModel
)


@dataclass
class RoleAggregate(CoreAggregate):
    model: RoleDataModel

    @event("AppendPermission")
    def append_permission(self, permission: PermissionsEnum):
        if isinstance(permission, PermissionsEnum):
            if permission not in self.model.permissions:
                self.model.permissions.append(permission)
            else:
                raise PermissionError(f"{permission} Already Present in Permissions")

        else:
            raise TypeError(f"Must be of type: {PermissionsEnum}")

        def remove_permission(self, permission: PermissionsEnum):
            self.trigger_event(self.RemovePermissionEvent, permission=permission)

        class RemovePermissionEvent(AggregateEvent):
            permission: PermissionsEnum

            def apply(self, aggregate: 'RoleAggregate') -> None:
                if self.permission in aggregate.model.permissions:
                    aggregate.model.permissions.remove(self.permission)
                else:
                    raise PermissionError(f"{self.permission} not in permission list")

    @event("RemovePermission")
    def remove_permission(self, permission: PermissionsEnum):
        if permission in self.model.permissions:
            self.model.permissions.remove(permission)

        else:
            raise PermissionError(f"{permission} Not present in list")


@dataclass
class UserAccountAggregate(CoreAggregate):
    model: UserDataModel
    role_mapping: Dict[UUID, 'RoleAggregate']

    @event("UpdateFirstName")
    def update_first_name(self, value):
        self.model.first_name = value

    @event("UpdateLastName")
    def update_last_name(self, value):
        self.model.last_name = value

    @event("UpdateEmail")
    def update_email(self, value):
        self.model.email = value

    @event("AddRoleEvent")
    def add_role(self, role: "RoleAggregate"):
        self.role_mapping[role.id] = role

    @event("RemoveRoleEvent")
    def remove_role(self, role: "RoleAggregate"):
        self.role_mapping.pop(role.id)


@dataclass
class ChildAggregate(UserAccountAggregate):
    model: ChildDataModel

    @event("UpdateGender")
    def update_gender(self, value: GenderEnum):
        if isinstance(value, GenderEnum):
            self.model.gender = value
        else:
            raise TypeError(f"Must be of type: {GenderEnum}")

    @event("UpdateAge")
    def update_age(self, value: int):
        self.model.age = value

    @event("UpdateGrade")
    def update_grade(self, value: int):
        if value > 12:
            raise ValueError("Invalid Value Provided, value must be < 12")

        self.model.age = value


@dataclass
class AdultAggregate(UserAccountAggregate):
    model: AdultDataModel


@dataclass
class FamilyAggregate(CoreAggregate):
    model: FamilyDataModel
    _children_mapping: Dict[UUID, 'ChildAggregate'] = field(default_factory=dict)
    _parent_mapping: Dict[UUID, 'AdultAggregate'] = field(default_factory=dict)

    def get_child(self, child: 'ChildAggregate'):
        return self._children_mapping.get(child.id)

    def get_parent(self, parent: 'AdultAggregate'):
        return self._parent_mapping.get(parent.id)

    @event("AddChild")
    def add_child(self, child: 'ChildAggregate'):
        self._children_mapping[child.id] = child

    @event("RemoveChild")
    def remove_child(self, child: 'ChildAggregate'):
        self._children_mapping.pop(child.id)

    @event("AddParent")
    def add_parent(self, parent: 'AdultAggregate'):
        self._parent_mapping[parent.id] = parent

    @event("RemoveParent")
    def remove_parent(self, parent: 'AdultAggregate'):
        self._parent_mapping.pop(parent.id)

from dataclasses import dataclass, field
from typing import Dict, List
from uuid import UUID

from eventsourcing.domain import event, Aggregate
from src.domains.core_domain import CoreAggregate
from src.enums import (
    PermissionsEnum,
    GenderEnum

)


@dataclass
class RoleAggregate(Aggregate):
    name: str
    permissions: List[PermissionsEnum]

    @event("AppendPermission")
    def append_permission(self, permission: PermissionsEnum):
        if isinstance(permission, PermissionsEnum):
            if permission not in self.permissions:
                self.permissions.append(permission)
            else:
                raise PermissionError(f"{permission} Already Present in Permissions")

        else:
            raise TypeError(f"Must be of type: {PermissionsEnum}")

    @event("RemovePermission")
    def remove_permission(self, permission: PermissionsEnum):
        if permission in self.permissions:
            self.permissions.remove(permission)

        else:
            raise PermissionError(f"{permission} Not present in list")


@dataclass
class UserAccountAggregate(CoreAggregate):
    first_name: str
    last_name: str
    email: str
    roles: List[UUID]

    @event("UpdateFirstName")
    def update_first_name(self, value):
        self.first_name = value

    @event("UpdateLastName")
    def update_last_name(self, value):
        self.last_name = value

    @event("UpdateEmail")
    def update_email(self, value):
        self.email = value

    @event("AddRoleEvent")
    def add_role(self, role: "RoleAggregate"):
        self.roles.append(role.id)

    @event("RemoveRoleEvent")
    def remove_role(self, role: "RoleAggregate"):
        self.roles.remove(role.id)


@dataclass
class ChildAggregate(UserAccountAggregate):
    gender: GenderEnum
    age: int
    grade: int

    @event("UpdateGender")
    def update_gender(self, value: GenderEnum):
        if isinstance(value, GenderEnum):
            self.gender = value
        else:
            raise TypeError(f"Must be of type: {GenderEnum}")

    @event("UpdateAge")
    def update_age(self, value: int):
        self.age = value

    @event("UpdateGrade")
    def update_grade(self, value: int):
        if value > 12:
            raise ValueError("Invalid Value Provided, value must be < 12")

        self.age = value


@dataclass
class AdultAggregate(UserAccountAggregate):
    roles: List[UUID]


@dataclass
class FamilyAggregate(Aggregate):
    name: str
    alias: str = field(default_factory=str)
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

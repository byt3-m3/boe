from dataclasses import dataclass
from typing import List
from uuid import UUID

from eventsourcing.domain import event, Aggregate
from src.domains.core_domain import CoreAggregate
from src.enums import (
    PermissionsEnum,
    GenderEnum

)
from src.utils.core_utils import make_id


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

    @classmethod
    def create(cls, first_name, last_name, email, roles):
        _id = make_id(
            domain="users",
            key=f"{email}"
        )
        return cls._create(
            event_class=cls.Created,
            id=_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            roles=roles
        )

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
    alias: str
    parents: List[UUID]
    children: List[UUID]

    @event("AppendChild")
    def append_child(self, aggregate_id: UUID):
        if aggregate_id not in self.children:
            self.children.append(aggregate_id)

    @event("RemoveChild")
    def remove_child(self, aggregate_id: UUID):
        self.children.remove(aggregate_id)

    @event("AppendParent")
    def append_parent(self, aggregate_id: UUID):
        if aggregate_id not in self.parents:
            self.parents.append(aggregate_id)

    @event("RemoveParent")
    def remove_parent(self, aggregate_id: UUID):
        self.parents.remove(aggregate_id)

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


@dataclass(frozen=True)
class ChildReadModel:
    fist_name: str
    last_name: str
    email: str


@dataclass
class RoleAggregate(Aggregate):
    name: str
    permissions: List[PermissionsEnum]

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "permissions": [permission.value for permission in self.permissions]
        }

    @classmethod
    def deserialize(cls, data):
        return {
            "name": data.get("name"),
            "permissions": [PermissionsEnum(permission) for permission in data.get("permissions")]
        }

    @classmethod
    def create(cls, name, permissions):
        if not permissions:
            permissions = []

        return cls._create(
            event_class=cls.Created,
            id=make_id(domain="users", key=f'{name}'),
            name=name,
            permissions=permissions
        )

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
    account_id: UUID

    def serialize(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "roles": self.roles,
            "account_id": self.account_id,
        }

    @classmethod
    def create(cls, first_name, last_name, email, roles) -> 'UserAccountAggregate':
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
            roles=roles,
            account_id=None

        )

    @event("SetAccountID")
    def set_account_id(self, account_id: UUID):
        self.account_id = account_id

    @event("AddRoleEvent")
    def add_role(self, role_id: UUID):
        self.roles.append(role_id)

    @event("RemoveRoleEvent")
    def remove_role(self, role: "RoleAggregate"):
        self.roles.remove(role.id)


@dataclass
class ChildAggregate(UserAccountAggregate):
    gender: GenderEnum
    age: int
    grade: int

    def serialize(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "roles": self.roles,
            "account_id": self.account_id,
            "gender": self.gender.value,
            "age": self.age,
            "grade": self.grade
        }

    @classmethod
    def create(cls, first_name, last_name, email, gender, age, grade):
        _id = make_id(
            domain="users",
            key=f"{email}"
        )
        return cls._create(
            account_id=None,
            event_class=cls.Created,
            id=_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            gender=gender,
            age=age,
            grade=grade,
            roles=[]
        )

    @event("UpdateGrade")
    def update_grade(self, value: int):
        if value > 12:
            raise ValueError("Invalid Value Provided, value must be < 12")

        self.age = value


@dataclass
class AdultAggregate(UserAccountAggregate):
    pass


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

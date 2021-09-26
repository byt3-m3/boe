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
    related_account_id: UUID

    def serialize(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "roles": self.roles,
            "related_account_id": self.related_account_id,
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
            related_account_id=None

        )

    @event
    def set_related_account_id(self, account_id: UUID):
        self.related_account_id = account_id

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
    task_id_list: List[UUID]

    def serialize(self) -> dict:
        return {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "roles": self.roles,
            "related_account_id": self.related_account_id,
            "gender": self.gender.value,
            "age": self.age,
            "grade": self.grade,
            "task_list": [str(_id) for _id in self.task_id_list]
        }

    @classmethod
    def create(cls, first_name, last_name, email, gender, age, grade):
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
            gender=gender,
            task_id_list=[],
            age=age,
            grade=grade,
            roles=[],
            related_account_id=None,
        )

    @event("UpdateGrade")
    def update_grade(self, value: int):
        if value > 12:
            raise ValueError("Invalid Value Provided, value must be < 12")

        self.age = value

    @event
    def add_task_id(self, task_id: UUID):
        if isinstance(task_id, UUID):
            if task_id not in self.task_id_list:
                self.task_id_list.append(task_id)
            else:
                raise ValueError(f"Value: {task_id} Already Present in List.")

        else:
            raise TypeError(f"Invalid Type, Expected {UUID}")

    @event
    def remove_task_id(self, task_id: UUID):
        if task_id in self.task_id_list:
            self.task_id_list.remove(task_id)


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

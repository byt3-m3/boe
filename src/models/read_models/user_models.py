from dataclasses import dataclass
from uuid import UUID
from typing import List
from src.enums import GenderEnum, PermissionsEnum
from src.models.read_models import ReadModel


@dataclass(frozen=True)
class RoleReadModel:
    name: str
    permissions: List[PermissionsEnum]

    @staticmethod
    def encode(data):
        _permissions = data.get("permissions", [])
        if len(_permissions) > 0:
            _permissions= [
                PermissionsEnum(permission) for permission in data.get("permissions") if permission
            ]

        return RoleReadModel(
            name=data.get("name"),
            permissions=_permissions
        )


@dataclass(frozen=True)
class ChildReadModel(ReadModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    gender: GenderEnum
    age: int
    grade: int

    @staticmethod
    def encode(data):
        return ChildReadModel(
            id=data.get("_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            gender=GenderEnum(data.get("gender")),
            age=data.get("age"),
            grade=data.get("grade")
        )

@dataclass(frozen=True)
class UserAccountReadModel(ReadModel):
    id: UUID
    first_name: str
    last_name: str
    email: str
    @staticmethod
    def encode(data):
        return UserAccountReadModel(
            id=data.get("_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
        )
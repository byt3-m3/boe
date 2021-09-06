from dataclasses import dataclass

from src.enums import PermissionsEnum, GenderEnum


@dataclass
class UserModel:
    first_name: str
    last_name: str
    email: str
    roles: List[RoleModel]


@dataclass
class RoleModel:
    name: str
    permissions: List[PermissionsEnum]


@dataclass
class ParentModel(UserModel):
    pass


@dataclass
class ChildModel(UserModel):
    gender: GenderEnum
    age: int
    grade: str
    nationality: str

from dataclasses import dataclass
from typing import List
from src.enums import PermissionsEnum, GenderEnum


@dataclass
class RoleDataModel:
    name: str



@dataclass
class UserDataModel:
    first_name: str
    last_name: str
    email: str


@dataclass
class ChildDataModel(UserDataModel):
    gender: GenderEnum
    age: int
    grade: int


@dataclass
class AdultDataModel(UserDataModel):
    pass


@dataclass
class FamilyDataModel:
    name: str
    alias: str = None

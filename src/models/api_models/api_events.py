from dataclasses import dataclass
from src.enums import GenderEnum

@dataclass(frozen=True)
class CreateTaskRequest:
    name: str
    description: str
    value: str

@dataclass(frozen=True)
class CreatChildRequest:
    first_name: str
    last_name: str
    email: str
    gender: GenderEnum
    age: int
    grade: int

@dataclass(frozen=True)
class CreateAdultRequest:
    first_name: str
    last_name: str
    email: str
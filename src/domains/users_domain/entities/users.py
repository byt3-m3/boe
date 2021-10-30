from dataclasses import dataclass
from typing import List
from uuid import UUID

from eventsourcing.domain import Aggregate, event
from src.enums import GenderEnum


@dataclass
class UserAccount(Aggregate):
    first_name: str
    last_name: str
    roles: List[UUID]

    @event
    def append_role(self, role_id: UUID):
        assert role_id not in self.roles
        self.roles.append(role_id)

    @event
    def remove_role(self, role_id: UUID):
        if role_id in self.roles:
            self.roles.remove(role_id)


@dataclass
class ChildAccount(UserAccount):
    age: int
    gender: GenderEnum

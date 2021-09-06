from src.domains.core_domain import CoreAggregate
from dataclasses import  dataclass


@dataclasses
class FamilyAggregate(CoreAggregate):
    name: str
    description: str


@dataclasses
class UserAggregate(CoreAggregate):
    name: str
    description: str
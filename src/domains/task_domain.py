from src.domains.core_domain import CoreAggregate
from dataclasses import  dataclass




@dataclasses
class TaskAggregate(CoreAggregate):
    name: str
    description: str
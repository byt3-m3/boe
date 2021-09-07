from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class TaskDataModel:
    name: str
    description: str
    assign_date: datetime
    due_date: datetime
    is_complete: bool = False
    attachment: bytes = field(default_factory=bytes)


@dataclass
class TaskItemDataModel:
    name: str
    description: str

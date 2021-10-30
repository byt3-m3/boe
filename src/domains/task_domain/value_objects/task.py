import uuid
from dataclasses import dataclass, field


@dataclass()
class TaskItem:
    id: uuid.UUID
    name: str
    description: str
    is_complete: bool = field(default=False)

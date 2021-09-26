import datetime
from dataclasses import dataclass, field
from typing import List
from uuid import UUID

from eventsourcing.domain import Aggregate, event


@dataclass
class TaskItem(Aggregate):
    name: str
    description: str
    is_complete: bool = field(default=False)

    @event
    def set_complete(self):
        self.is_complete = True


@dataclass
class TaskAggregate(Aggregate):
    name: str
    description: str
    due_date: int
    value: int = field(init=True)
    attachments: List[bytes] = field(default_factory=list)
    items: List[UUID] = field(default=list)
    is_complete: bool = field(default=False)
    is_validated: bool = field(default=False)
    assignee: UUID = field(default=None)

    def serialize(self):
        return {
            "name": self.name,
            "description": self.description,
            "due_date": self.due_date,
            "attachments": self.attachments,
            "items": self.items,
            "is_complete": self.is_complete,
            "assignee": self.assignee,
        }

    @event
    def append_item(self, task_item_id: UUID):
        if task_item_id not in self.items:
            self.items.append(task_item_id)

    @event
    def remove_item(self, task_item_id: UUID):
        if task_item_id in self.items:
            self.items.remove(task_item_id)

    @event
    def set_not_complete(self):
        if self.is_complete:
            self.is_complete = False

    @event
    def set_complete(self):
        if self.is_validated:
            if not self.is_complete:
                self.is_complete = True

    @event
    def set_validated(self):
        if not self.is_validated:
            self.is_validated = True

    @event
    def invalidate(self):
        if self.is_validated:
            self.is_validated = False

    @event
    def update_assign_date(self):
        self.assign_date = datetime.datetime.now()

    @event
    def append_attachment(self, data: bytes):
        if data not in self.attachments:
            self.attachments.append(data)

    @event
    def remove_attachment(self, data: bytes):
        if data in self.attachments:
            self.attachments.remove(data)

    @event
    def update_due_date(self, timestamp: int):
        self.due_date = timestamp

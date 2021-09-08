import datetime
from dataclasses import dataclass, field
from typing import List

from eventsourcing.domain import Aggregate, event
from uuid import UUID


@dataclass
class TaskItem(Aggregate):
    name: str
    description: str


@dataclass
class TaskAggregate(Aggregate):
    name: str
    description: str
    assign_date: datetime
    due_date: datetime
    assignee: UUID
    attachments: List[bytes] = field(default_factory=list)
    items: List[UUID] = field(default_factory=list)
    is_complete: bool = field(default=False)

    @event
    def append_item(self, task_item_id: UUID):
        if task_item_id not in self.items:
            self.items.append(task_item_id)

    @event
    def remove_item(self, task_item_id: UUID):
        if task_item_id in self.items:
            self.items.remove(task_item_id)

    @event
    def update_assignee(self, child_id: UUID):
        self.assignee = child_id
        self.update_assign_date()

    @event
    def set_not_complete(self):
        if self.is_complete:
            self.is_complete = False

    @event
    def set_complete(self):
        if not self.is_complete:
            self.is_complete = True

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
    def update_due_date(self, date: datetime.datetime):
        self.due_date = date

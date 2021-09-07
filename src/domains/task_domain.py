import datetime
from dataclasses import dataclass, field
from typing import List

from eventsourcing.domain import Aggregate, event
from src.domains.user_domain import ChildAggregate
from src.models.task_models import TaskDataModel, TaskItemDataModel


@dataclass
class TaskItem(Aggregate):
    model: TaskItemDataModel


@dataclass
class TaskAggregate(Aggregate):
    model: TaskDataModel
    assignee: ChildAggregate
    items: List[TaskItem] = field(default_factory=list)

    @event
    def append_item(self, task_item: TaskItem):
        if task_item not in self.items:
            self.items.append(task_item)

    @event
    def remove_item(self, task_item: TaskItem):
        if task_item in self.items:
            self.items.remove(task_item)

    @event
    def update_assignee(self, child: ChildAggregate):
        self.assignee = child
        self.update_assign_date()

    @event
    def set_not_complete(self):
        self.model.is_complete = False

    @event
    def set_complete(self):
        if not self.model.is_complete:
            self.model.is_complete = True

    @event
    def update_assign_date(self):
        self.model.assign_date = datetime.datetime.now()

    @event
    def update_attachment(self, data: bytes):
        self.model.attachment = data

    @event
    def update_due_date(self, date: datetime.datetime):
        self.model.due_date = date

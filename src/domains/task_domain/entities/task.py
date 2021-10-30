from dataclasses import dataclass, field
from typing import List
from uuid import UUID

from cbaxter1988_utils import log_utils
from eventsourcing.domain import Aggregate, event
from src.domains.task_domain.value_objects.task import TaskItem
from src.enums import TaskState

logger = log_utils.get_logger(__name__)


@dataclass
class Task(Aggregate):
    name: str
    description: str
    value: int
    items: List[TaskItem] = field(default_factory=list)
    state: TaskState = TaskState.ENABLED
    assignee_id: UUID = None
    due_date: int = None

    @event
    def set_state(self, state: TaskState):
        if self.state == TaskState.ENABLED:
            if state == TaskState.DISABLED:
                self.state = state
                return

            if state == TaskState.ASSIGNED:
                self.state = state
                return

        if self.state == TaskState.ASSIGNED:

            if state == TaskState.OVER_DUE:
                self.state = state
                return

            if state == TaskState.ENABLED:
                self.state = state
                return

            if state == TaskState.WORK_COMPLETED:
                self.state = state
                return

        if self.state == TaskState.OVER_DUE:
            if state == TaskState.ASSIGNED:
                self.state = state
                return

            if state == TaskState.WORK_COMPLETED:
                self.state = state
                return

        if self.state == TaskState.DISABLED:
            if state == TaskState.ENABLED:
                self.state = state
                return

        err_msg = f"Invalid Transition; Current State: {self.state} - Desired State: {state}"
        logger.error(err_msg)
        raise ValueError(err_msg)

    @event
    def add_item(self, task_item: TaskItem):
        assert task_item not in self.items, "Task Is Present in List"
        self.items.append(task_item)

    @event
    def mark_item_complete(self, item_id):
        for item in self.items:
            if item.id == item_id:
                item.is_complete = True

    @event
    def mark_item_not_complete(self, item_id):
        for item in self.items:
            if item.id == item_id:
                item.is_complete = False

    @event
    def modify_due_date(self, due_date_ts: int):
        self.due_date = int(due_date_ts)

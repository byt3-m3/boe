from typing import List
from uuid import UUID, uuid4

from src.domains.task_domain.entities.task import Task, TaskState
from src.domains.task_domain.value_objects.task import TaskItem


class TaskDomainFactory:

    @staticmethod
    def build_task_item(name, description, is_complete: bool = False, _id=None) -> TaskItem:
        if _id is None:
            _id = uuid4()

        return TaskItem(
            name=name,
            description=description,
            is_complete=is_complete,
            id=_id
        )

    @staticmethod
    def build_task(
            name: str,
            description: str,
            value: int,
            due_date: int,
            assignee_id: UUID,
            state: TaskState = TaskState.ASSIGNED,
            items: List[TaskItem] = None,
    ) -> Task:
        if items is None:
            items = []

        return Task(
            description=description,
            name=name,
            value=value,
            due_date=due_date,
            items=items,
            assignee_id=assignee_id,
            state=state,
        )

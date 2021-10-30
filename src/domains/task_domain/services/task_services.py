from typing import List
from uuid import UUID

from cbaxter1988_utils import log_utils
from src.domains.task_domain.entities.task import Task, TaskItem
from src.domains.task_domain.factories import TaskDomainFactory
from src.enums import TaskState
from src.services.base import Service

domain_factory = TaskDomainFactory()

logger = log_utils.get_logger(__name__)


class TaskQueryService(Service):
    @staticmethod
    def query_task(query: dict):
        pass


class TaskManagementService(Service):

    @staticmethod
    def create_task(
            assignee_id: UUID,
            name: str,
            description: str,
            due_date: int,
            value: int,
            state: TaskState,
            items: List[TaskItem],
    ) -> Task:
        return domain_factory.build_task(
            name=name,
            due_date=due_date,
            assignee_id=assignee_id,
            value=value,
            description=description,
            state=state,
            items=items,
        )

    @staticmethod
    def create_task_item(name: str, description: str, is_complete=False):
        return domain_factory.build_task_item(
            name=name,
            description=description,
            is_complete=is_complete
        )

    @staticmethod
    def set_task_state(task: Task, state: TaskState):
        task.set_state(state=state)

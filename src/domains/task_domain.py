from src.domains.core_domain import CoreAggregate
from src.models.task_models import TaskDataModel


@dataclasses
class TaskAggregate(CoreAggregate):
    model: TaskDataModel

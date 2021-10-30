import pytest
from src.domains.task_domain.services.task_services import TaskManagementService
from src.enums import TaskState


def test_task_management_service_set_task_state_completed(task):
    service = TaskManagementService()
    service.set_task_state(task=task, state=TaskState.WORK_COMPLETED)

    assert task.state == TaskState.WORK_COMPLETED
    assert len(task.pending_events) == 2


def test_task_management_service_set_task_state_over_due(task):
    service = TaskManagementService()

    service.set_task_state(task=task, state=TaskState.OVER_DUE)

    assert task.state == TaskState.OVER_DUE
    assert len(task.pending_events) == 2


def test_task_management_service_set_task_state(task):
    service = TaskManagementService()

    with pytest.raises(ValueError):
        service.set_task_state(task=task, state=TaskState.AWARDED)

    assert task.state == TaskState.ASSIGNED
    assert len(task.pending_events) == 1

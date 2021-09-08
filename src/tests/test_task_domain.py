from datetime import timedelta

from pytest import fixture
from src.domains.task_domain import TaskAggregate, TaskItem
from src.utils.core_utils import clone_item


@fixture
def task_aggregate(child_aggregate, test_name, test_email, test_datetime, test_description):
    return TaskAggregate(
        name=test_name,
        description=test_description,
        # assign_date=clone_item(test_datetime),
        due_date=clone_item(test_datetime),
        assignee=child_aggregate.id
    )


@fixture
def task_item_aggregate(test_name, test_description):
    return TaskItem(
        name=test_name,
        description=test_description,
    )


def test_task_aggregate_update_assignee(task_aggregate, child_aggregate):
    task_aggregate.update_assignee(child_id=child_aggregate.id)
    events = task_aggregate.collect_events()

    assert isinstance(events[2], task_aggregate.UpdateAssignee)
    assert isinstance(events[1], task_aggregate.UpdateAssignDate)
    assert task_aggregate.assignee is child_aggregate.id


def test_task_aggregate_set_complete(task_aggregate):
    assert task_aggregate.is_complete is False
    task_aggregate.set_complete()
    assert task_aggregate.is_complete is True


def test_task_aggregate_set_not_complete(task_aggregate):
    task_aggregate.set_complete()
    assert task_aggregate.is_complete is True
    task_aggregate.set_not_complete()
    assert task_aggregate.is_complete is False


def test_task_aggregate_update_assign_date(task_aggregate, test_datetime):
    task_aggregate.update_assign_date()
    assert task_aggregate.assign_date > test_datetime


def test_task_aggregate_append_attachment(task_aggregate, test_byte_data):
    task_aggregate.append_attachment(data=test_byte_data)
    assert test_byte_data in task_aggregate.attachments
    assert len(task_aggregate.attachments) == 1


def test_task_aggregate_remove_attachment(task_aggregate, test_byte_data):
    task_aggregate.append_attachment(data=test_byte_data)
    task_aggregate.remove_attachment(data=test_byte_data)
    assert test_byte_data not in task_aggregate.attachments
    assert len(task_aggregate.attachments) == 0


def test_task_aggregate_update_due_date(task_aggregate, test_datetime):
    due_date = clone_item(test_datetime)
    delta = timedelta(days=5)
    due_date = due_date + delta
    task_aggregate.update_due_date(date=due_date)
    assert task_aggregate.due_date is due_date


def test_task_aggregate_append_item(task_aggregate, task_item_aggregate):
    task_aggregate.append_item(task_item_id=task_item_aggregate.id)
    assert len(task_aggregate.items) == 1


def test_task_aggregate_remove_item(task_aggregate, task_item_aggregate):
    task_aggregate.append_item(task_item_id=task_item_aggregate.id)
    task_aggregate.remove_item(task_item_id=task_item_aggregate.id)
    assert len(task_aggregate.items) == 0

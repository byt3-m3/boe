from datetime import timedelta

from pytest import fixture
from src.domains.task_domain import TaskAggregate, TaskItem
from src.models.task_models import TaskDataModel, TaskItemDataModel
from src.utils.core_utils import clone_item


@fixture
def task_data_model(test_name, test_email, test_datetime, test_description):
    return TaskDataModel(
        name=test_name,
        description=test_description,
        assign_date=clone_item(test_datetime),
        due_date=clone_item(test_datetime),

    )


@fixture
def task_item_data_model(test_name, test_description):
    return TaskItemDataModel(
        name=test_name,
        description=test_description,

    )


@fixture
def task_aggregate(task_data_model, child_aggregate):
    return TaskAggregate(
        model=task_data_model,
        assignee=child_aggregate
    )


@fixture
def task_item_aggregate(task_item_data_model):
    return TaskItem(
        model=task_item_data_model
    )


def test_task_aggregate_update_child(task_aggregate, child_aggregate):
    child = clone_item(child_aggregate)
    child.update_first_name("updated_fname")
    child.update_last_name("updated_lname")
    task_aggregate.update_assignee(child=child)
    events = task_aggregate.collect_events()

    assert isinstance(events[2], task_aggregate.UpdateAssignee)
    assert isinstance(events[1], task_aggregate.UpdateAssignDate)
    assert task_aggregate.assignee is child
    assert task_aggregate.assignee.first_name == "updated_fname"


def test_task_aggregate_set_complete(task_aggregate):
    assert task_aggregate.model.is_complete is False
    task_aggregate.set_complete()
    assert task_aggregate.model.is_complete is True


def test_task_aggregate_set_not_complete(task_aggregate):
    task_aggregate.set_complete()
    assert task_aggregate.model.is_complete is True
    task_aggregate.set_not_complete()
    assert task_aggregate.model.is_complete is False


def test_task_aggregate_update_asign_date(task_aggregate, test_datetime):
    assert task_aggregate.model.assign_date == test_datetime
    task_aggregate.update_assign_date()
    assert task_aggregate.model.assign_date > test_datetime


def test_task_aggregate_update_attachment(task_aggregate, test_byte_data):
    task_aggregate.update_attachment(data=test_byte_data)
    assert task_aggregate.model.attachment == test_byte_data


def test_task_aggregate_update_due_date(task_aggregate, test_datetime):
    due_date = clone_item(test_datetime)
    delta = timedelta(days=5)
    due_date = due_date + delta
    task_aggregate.update_due_date(date=due_date)
    assert task_aggregate.model.due_date is due_date


def test_task_aggregate_append_item(task_aggregate, task_item_aggregate):
    task_aggregate.append_item(task_item=task_item_aggregate)
    assert len(task_aggregate.items) == 1

def test_task_aggregate_remove_item(task_aggregate, task_item_aggregate):
    task_aggregate.append_item(task_item=task_item_aggregate)
    task_aggregate.remove_item(task_item=task_item_aggregate)
    assert len(task_aggregate.items) == 0

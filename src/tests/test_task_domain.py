from pytest import fixture
from src.models.task_models import TaskDataModel
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
def task_item_data_model(test_name, test_email, test_datetime, test_description):
    return TaskDataModel(
        name=test_name,
        description=test_description,

    )


@fixture
def task_aggregate(task_data_model):
    return TaskDataModel(
        model=task_data_model
    )

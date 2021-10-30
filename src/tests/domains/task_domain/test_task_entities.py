import datetime

from src.enums import TaskState


def test_task_state_changes(task):
    assert task.state is TaskState.ASSIGNED

    task.set_state(state=TaskState.ENABLED)
    assert task.state is TaskState.ENABLED

    task.set_state(state=TaskState.DISABLED)
    assert task.state is TaskState.DISABLED


def test_task_append_item(task, task_item):
    assert len(task.items) == 0
    task.add_item(task_item)

    assert len(task.items) == 1
    print(task.items)


def test_task_mark_item_complete(task, task_item):
    task.add_item(task_item)

    task.mark_item_complete(item_id=task_item.id)
    assert task_item.is_complete


def test_task_mark_item_not_complete(task, task_item):
    task.add_item(task_item)

    task.mark_item_not_complete(item_id=task_item.id)
    assert not task_item.is_complete


def test_task_modify_due_date(task):
    new_due_date = int(datetime.datetime.now().timestamp())
    task.modify_due_date(due_date_ts=new_due_date)

    assert task.due_date == new_due_date
    print(task.pending_events)

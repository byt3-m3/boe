from pytest import fixture
from src.applications.boe_app import (
    BOEApplication,
    UserAccountAggregate,
    TaskAggregate,
    BankAccount
)
from src.enums import (
    PermissionsEnum,
    AccountStatusEnum,
    GenderEnum
)


@fixture
def boe_application():
    return BOEApplication()


@fixture
def boe_appication_w_account():
    app = BOEApplication()
    app.create_new_account(
        owner_first_name="t",
        owner_last_name='test',
        role_name='TestRole',
        permissions=[PermissionsEnum.ADMIN],
        owner_email='test.com',
        owner_age=5,
        owner_grade=5,
        owner_gender=GenderEnum.MALE
    )
    return app


def _test_boe_application_create_new_accout(boe_application):
    account = boe_application.create_new_account(
        owner_first_name="t",
        owner_last_name='test',
        owner_email='test.com',
        owner_age=5,
        owner_grade=5,
        owner_gender=GenderEnum.MALE,
        admin_first_name='test',
        admin_last_name='test',
        admin_email='test',
    )
    assert isinstance(account, BankAccount)


def test_boe_application_set_account_inactive(boe_application):
    account = boe_application.create_new_account(
        owner_first_name="t",
        owner_last_name='test',
        owner_email='test.com',
        owner_age=5,
        owner_grade=5,
        owner_gender=GenderEnum.MALE,
        admin_first_name='test',
        admin_last_name='test',
        admin_email='test',
    )

    boe_application.set_account_inactive(aggregate_id=account.id)
    _account = boe_application.get_account(aggregate_id=account.id)
    _account: BankAccount

    assert _account.status == AccountStatusEnum.INACTIVE


def test_boe_app_create_new_parent(boe_application):
    parent = boe_application.create_new_parent(
        first_name='test',
        last_name='test',
        email='test@gmail.com',
        role_name='test_role',
        permissions=[PermissionsEnum.ADMIN]
    )
    assert isinstance(parent, UserAccountAggregate)


def test_boe_app_create_task(boe_application, test_name, test_description, test_datetime):
    task = boe_application.create_task(
        name=test_name,
        description=test_description,
        due_date=test_datetime
    )

    assert isinstance(task, TaskAggregate)
    assert task == boe_application.repository.get(aggregate_id=task.id)

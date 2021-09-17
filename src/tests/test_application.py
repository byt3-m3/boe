from uuid import UUID

from pytest import fixture
from src.applications.boe_app import (
    BOEApplication,
    TaskAggregate,
    RoleAggregate
)
from src.enums import (
    PermissionsEnum,
    AccountStatusEnum,
    GenderEnum,
    TransactionMethodEnum
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


def test_boe_application_create_new_accout(boe_application):
    result_mapping = boe_application.create_new_account(
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
    assert isinstance(result_mapping, dict)
    assert not False in [isinstance(_id, UUID) for _id in result_mapping.values()]


def test_boe_app_create_new_parent(boe_application):
    result_mapping = boe_application.create_new_parent(
        first_name='test',
        last_name='test',
        email='test@gmail.com',
        role_name='test_role',
        permissions=[PermissionsEnum.ADMIN]
    )
    assert isinstance(result_mapping, dict)

    assert not False in [isinstance(_id, UUID) for _id in result_mapping.values()]


def test_boe_app_create_task(boe_application, test_name, test_description, test_datetime):
    task_id = boe_application.create_task(
        name=test_name,
        description=test_description,
        due_date=test_datetime
    )

    assert isinstance(task_id, UUID)
    assert task_id == boe_application.repository.get(aggregate_id=task_id).id


def test_app_change_account_balance(boe_application):
    result_mapping = boe_application.create_new_account(
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
    account_id = result_mapping['account_id']
    boe_application.change_account_balance(
        account_id=account_id,
        val=50,
        transaction_method=TransactionMethodEnum.ADD.value
    )

    account = boe_application.get_account(account_id=account_id)
    assert account.balance == 50


def test_app_change_account_status(boe_application):
    result_mapping = boe_application.create_new_account(
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
    account_id = result_mapping['account_id']

    boe_application.change_account_status(account_id=account_id, status=AccountStatusEnum.INACTIVE.value)

    account = boe_application.get_account(account_id=account_id)
    assert account.status == AccountStatusEnum.INACTIVE


def test_app_create_role_aggeragates(boe_application):
    role_id = boe_application.create_role(name='TestRole', permissions=[PermissionsEnum.ADMIN])
    role = boe_application.get_role_aggeragates(role_ids=[role_id])[0]
    assert isinstance(role, RoleAggregate)

import os
from uuid import UUID

from pytest import fixture
from src.domains.bank_domain.factories import BankDomainFactory
from src.domains.store_domain.store_factories import StoreDomainFactory
from src.domains.task_domain.factories import TaskDomainFactory
from src.domains.users_domain.factories import UserDomainFactory
from src.enums import (
    PermissionsEnum,
    TransactionMethodEnum,
    GenderEnum
)
from tests.const import (
    TEST_NAME,
    TEST_FIRST_NAME,
    TEST_LAST_NAME,
    TEST_UUID,
    TEST_DESCRIPTION,
    TEST_TASK_VALUE,
    TEST_AGE,
    TEST_DUE_DATE_TS
)

user_domain_factory = UserDomainFactory()
bank_domain_factory = BankDomainFactory()
task_domain_factory = TaskDomainFactory()


@fixture(autouse=True)
def set_env():
    INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
    SQLITE_DBNAME = "_db/test_event_db"

    os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
    os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME


# User Domain Entities

@fixture
def admin_role():
    return user_domain_factory.build_account_role(
        role_name=TEST_NAME,
        permissions=[
            PermissionsEnum.ADMIN
        ]
    )


@fixture
def child_role():
    return user_domain_factory.build_account_role(
        role_name=TEST_NAME,
        permissions=[
            PermissionsEnum.Child
        ]
    )


@fixture
def user_account(admin_role):
    return user_domain_factory.build_user_account(
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        roles=[admin_role]
    )


@fixture
def child_account(admin_role):
    return user_domain_factory.build_child_account(
        first_name=TEST_FIRST_NAME,
        last_name=TEST_LAST_NAME,
        gender=GenderEnum.MALE,
        roles=[admin_role],
        age=TEST_AGE
    )


# Bank Domain Entities

@fixture
def bank_account():
    return bank_domain_factory.build_bank_account(
        owner_id=UUID(TEST_UUID),
        balance=0,
        overdraft_protection=True
    )


@fixture
def add_transaction():
    return bank_domain_factory.build_transaction(
        value=50,
        method=TransactionMethodEnum.ADD
    )


@fixture
def subtract_transaction():
    return bank_domain_factory.build_transaction(
        value=50,
        method=TransactionMethodEnum.SUBTRACT
    )


# Task Domain Entities

@fixture
def task():
    return TaskDomainFactory.build_task(
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        value=TEST_TASK_VALUE,
        due_date=TEST_DUE_DATE_TS,
        assignee_id=UUID(TEST_UUID),
    )


@fixture
def task_item():
    return TaskDomainFactory.build_task_item(
        name=TEST_NAME,
        description=TEST_DESCRIPTION,
        is_complete=False,
        _id=TEST_UUID
    )


@fixture
def inventory_item():
    return StoreDomainFactory.build_inventory_item(
        name="TEST_ITEM",
        quantity=10,
        price=5
    )


@fixture
def inventory():
    return StoreDomainFactory.build_empty_inventory()


@fixture
def store(inventory, inventory_item):
    inventory.add_item(inventory_item)

    return StoreDomainFactory.build_store(
        inventory=inventory
    )


@fixture
def store_transaction(inventory_item):
    return StoreDomainFactory.build_store_transaction(
        item_id=inventory_item.id,
        quantity=1
    )

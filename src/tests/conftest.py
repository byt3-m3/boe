from pytest import fixture
from src.domains.user_domain import (
    RoleAggregate,
    ChildAggregate,
    FamilyAggregate,
    UserAccountAggregate,
    AdultAggregate
)
from src.enums import PermissionsEnum, GenderEnum
from tests.const import (
    TEST_NAME,
    TEST_EMAIL,
    TEST_DATETIME,
    TEST_DESCRIPTION,
    TEST_BYTE_DATA
)


@fixture
def test_name():
    return TEST_NAME


@fixture
def test_email():
    return TEST_EMAIL


@fixture
def test_datetime():
    return TEST_DATETIME


@fixture
def test_description():
    return TEST_DESCRIPTION


@fixture
def test_byte_data():
    return TEST_BYTE_DATA


@fixture
def role_aggregate():
    yield RoleAggregate(
        name="test_role",
        permissions=[PermissionsEnum.ADMIN]
    )


@fixture
def child_aggregate(role_aggregate):
    return ChildAggregate(
        first_name="test_name",
        last_name="test_name",
        email="test@gmail.com",
        age=5,
        grade=3,
        gender=GenderEnum.MALE,
        roles=[role_aggregate.id]
    )


@fixture
def adult_aggregate(role_aggregate):
    yield AdultAggregate(
        first_name="test_name",
        last_name="test_name",
        email="test@gmail.com",
        roles=[role_aggregate.id]
    )


@fixture
def family_aggregate() -> FamilyAggregate:
    return FamilyAggregate(
        name="test_family_name"
    )


@fixture
def user_account_aggregate(role_aggregate):
    return UserAccountAggregate(
        first_name="test_name",
        last_name="test_name",
        email="test@gmail.com",
        roles=[role_aggregate.id]
    )

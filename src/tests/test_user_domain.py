from pytest import fixture
from src.domains.user_domain import (
    ChildAggregate,
    ChildDataModel,
    AdultAggregate,
    AdultDataModel,
    FamilyDataModel,
    FamilyAggregate,
    RoleAggregate
)
from src.models.user_models import RoleDataModel, PermissionsEnum
from src.enums import GenderEnum


@fixture
def role_data_model():
    yield RoleDataModel(
        name="test_role",
        permissions=[PermissionsEnum.ADMIN]
    )


@fixture
def role_aggregate_testable(role_data_model):
    yield RoleAggregate(
        model=role_data_model
    )


@fixture
def child_aggregate_testable(role_aggregate_testable):
    yield ChildAggregate(
        model=ChildDataModel(
            first_name="test_name",
            last_name="test_name",
            email="test@gmail.com",
            age=5,
            grade=3,
            nationality="USA",
            gender=GenderEnum.MALE

        ),
        role_mapping={
            role_aggregate_testable.id: role_aggregate_testable
        }
    )


@fixture
def adult_aggregate_testable(role_aggregate_testable):
    yield AdultAggregate(
        model=AdultDataModel(
            first_name="test_name",
            last_name="test_name",
            email="test@gmail.com",

        ),
        role_mapping={
            role_aggregate_testable.id: role_aggregate_testable
        }
    )


@fixture
def family_aggregate_testable(child_aggregate_testable, adult_aggregate_testable):
    yield FamilyAggregate(
        model=FamilyDataModel(
            name="test_family_name")

    )


def test_family_aggregate_add_child(family_aggregate_testable, child_aggregate_testable):
    child_aggregate = child_aggregate_testable
    family_aggregate = family_aggregate_testable
    family_aggregate: FamilyAggregate

    family_aggregate.add_child(child_aggregate)
    result = family_aggregate.children_mapping.get(child_aggregate_testable.id)

    assert isinstance(result, ChildAggregate)

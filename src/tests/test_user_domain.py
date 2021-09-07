import pytest
from pytest import fixture
from src.domains.user_domain import (
    ChildAggregate,
    ChildDataModel,
    AdultAggregate,
    AdultDataModel,
    FamilyDataModel,
    FamilyAggregate,
    UserAccountAggregate,
    UserDataModel,
    RoleAggregate
)
from src.enums import GenderEnum
from src.models.user_models import PermissionsEnum


@fixture
def user_data_model():
    return UserDataModel(
        first_name='test_first_name',
        last_name='test_last_name',
        email="test_email"
    )


@fixture
def child_aggregate_testable(role_aggregate):
    yield ChildAggregate(
        model=ChildDataModel(
            first_name="test_name",
            last_name="test_name",
            email="test@gmail.com",
            age=5,
            grade=3,
            gender=GenderEnum.MALE

        ),
        role_mapping={
            role_aggregate.id: role_aggregate
        }
    )


@fixture
def adult_aggregate_testable(role_aggregate):
    yield AdultAggregate(
        model=AdultDataModel(
            first_name="test_name",
            last_name="test_name",
            email="test@gmail.com",

        ),
        role_mapping={
            role_aggregate.id: role_aggregate
        }
    )


@fixture
def family_aggregate_testable(child_aggregate_testable, adult_aggregate_testable) -> FamilyAggregate:
    return FamilyAggregate(
        model=FamilyDataModel(
            name="test_family_name")
    )


@fixture
def user_account_aggregate_testable(role_aggregate, user_data_model):
    return UserAccountAggregate(
        model=user_data_model,
        role_mapping={
            role_aggregate.id: role_aggregate
        }
    )


def test_family_aggregate_add_child(family_aggregate_testable, child_aggregate_testable):
    child_aggregate = child_aggregate_testable
    family_aggregate_testable.add_child(child_aggregate)
    result = family_aggregate_testable.get_child(child=child_aggregate)
    assert isinstance(result, ChildAggregate)


def test_family_aggregate_remove_child(family_aggregate_testable, child_aggregate_testable):
    child_aggregate = child_aggregate_testable
    family_aggregate_testable.add_child(child_aggregate)
    family_aggregate_testable.remove_child(child_aggregate)
    result = family_aggregate_testable.get_child(child_aggregate_testable)
    assert result is None


def test_family_aggregate_add_parent(family_aggregate_testable, adult_aggregate_testable):
    parent = adult_aggregate_testable
    family_aggregate_testable.add_parent(parent)
    result = family_aggregate_testable.get_parent(parent)
    assert isinstance(result, AdultAggregate)


def test_family_aggregate_remove_parent(family_aggregate_testable, adult_aggregate_testable):
    parent = adult_aggregate_testable
    family_aggregate_testable.add_parent(parent)
    family_aggregate_testable.remove_parent(parent=parent)
    result = family_aggregate_testable.get_parent(parent)
    assert result is None


def test_user_account_aggregate_add_role(user_account_aggregate_testable, role_data_model):
    testable = user_account_aggregate_testable

    new_role = RoleAggregate(model=role_data_model, permissions=[PermissionsEnum.ADMIN])
    testable.add_role(new_role)

    actual = testable.role_mapping.get(new_role.id)

    assert isinstance(actual, RoleAggregate)


def test_user_account_aggregate_remove_role(user_account_aggregate_testable, role_data_model):
    testable = user_account_aggregate_testable

    new_role = RoleAggregate(model=role_data_model, permissions=[PermissionsEnum.ADMIN])
    testable.add_role(new_role)
    testable.remove_role(role=new_role)

    actual = testable.role_mapping.get(new_role.id)

    assert actual is None


def test_user_account_aggregate_change_first_name(user_account_aggregate_testable):
    subject = user_account_aggregate_testable
    subject.update_first_name("New Name")
    print(subject.collect_events())
    assert subject.model.first_name == "New Name"


def test_user_account_aggregate_update_email(user_account_aggregate_testable):
    subject = user_account_aggregate_testable
    subject.update_email("New Name")
    assert subject.model.email == "New Name"


def test_user_account_aggregate_update_last_name(user_account_aggregate_testable):
    subject = user_account_aggregate_testable
    subject.update_last_name("New Name")
    assert subject.model.last_name == "New Name"


def test_role_aggregate_append_permission(role_aggregate):
    testable = role_aggregate
    testable.append_permission(permission=PermissionsEnum.AccountAdminModifyPermissions)
    assert PermissionsEnum.AccountAdminModifyPermissions in testable.permissions


def test_role_aggregate_append_permission_2(role_aggregate):
    testable = role_aggregate
    with pytest.raises(PermissionError):
        testable.append_permission(permission=PermissionsEnum.ADMIN)


def test_role_aggregate_remove_permission(role_aggregate):
    testable = role_aggregate
    testable.remove_permission(permission=PermissionsEnum.ADMIN)
    assert PermissionsEnum.ADMIN not in testable.permissions
    assert len(testable.permissions) == 0


def test_role_aggregate_remove_permission_2(role_aggregate):
    testable = role_aggregate
    with pytest.raises(PermissionError):
        testable.remove_permission(permission=PermissionsEnum.AccountAddAccountAdmin)


def test_child_aggregate(child_aggregate_testable):
    subject = child_aggregate_testable
    FNAME = "Bugs"
    LNAME = "Bunny"
    EMAIL = "bugs@gmail.com"

    subject.update_first_name(value=FNAME)
    subject.update_last_name(value=LNAME)
    subject.update_email(value=EMAIL)
    subject.update_gender(value=GenderEnum.MALE)

    assert subject.model.first_name == FNAME
    assert subject.model.last_name == LNAME
    assert subject.model.email == EMAIL
    assert subject.model.gender == GenderEnum.MALE


def test_child_aggregate_update_grade_value_error(child_aggregate_testable):
    subject = child_aggregate_testable
    with pytest.raises(ValueError):
        subject.update_grade(13)

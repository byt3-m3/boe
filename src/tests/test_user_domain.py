from uuid import UUID

import pytest
from src.domains.user_domain import (
    RoleAggregate
)
from src.enums import GenderEnum, PermissionsEnum


def test_family_aggregate_append_child(family_aggregate, child_aggregate):
    family_aggregate.append_child(aggregate_id=child_aggregate.id)
    assert child_aggregate.id in family_aggregate.children


def test_family_aggregate_remove_child(family_aggregate, child_aggregate):
    family_aggregate.append_child(aggregate_id=child_aggregate.id)
    family_aggregate.remove_child(aggregate_id=child_aggregate.id)

    assert child_aggregate.id not in family_aggregate.children


def test_family_aggregate_apend_parent(family_aggregate, adult_aggregate):
    family_aggregate.append_parent(aggregate_id=adult_aggregate.id)

    assert adult_aggregate.id in family_aggregate.parents


def test_family_aggregate_remove_parent(family_aggregate, adult_aggregate):
    family_aggregate.append_parent(aggregate_id=adult_aggregate.id)
    family_aggregate.remove_parent(aggregate_id=adult_aggregate.id)

    assert adult_aggregate.id not in family_aggregate.parents


def test_user_account_aggregate_add_role(user_account_aggregate, role_aggregate):
    testable = user_account_aggregate

    new_role = RoleAggregate(name='test_role', permissions=[PermissionsEnum.ADMIN])
    testable.add_role(new_role)

    actual = testable.roles[0]

    assert isinstance(actual, UUID)


def test_user_account_aggregate_remove_role(user_account_aggregate, role_aggregate):
    testable = user_account_aggregate

    new_role = RoleAggregate(name='new_role', permissions=[PermissionsEnum.ADMIN])
    testable.add_role(new_role)
    testable.remove_role(role=new_role)

    assert len(testable.roles) == 1
    assert new_role not in testable.roles


def test_user_account_aggregate_change_first_name(user_account_aggregate):
    subject = user_account_aggregate
    subject.update_first_name("New Name")
    print(subject.collect_events())
    assert subject.first_name == "New Name"


def test_user_account_aggregate_update_email(user_account_aggregate):
    subject = user_account_aggregate
    subject.update_email("New Name")
    assert subject.email == "New Name"


def test_user_account_aggregate_update_last_name(user_account_aggregate):
    subject = user_account_aggregate
    subject.update_last_name("New Name")
    assert subject.last_name == "New Name"


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


def test_child_aggregate(child_aggregate):
    subject = child_aggregate
    FNAME = "Bugs"
    LNAME = "Bunny"
    EMAIL = "bugs@gmail.com"

    subject.update_first_name(value=FNAME)
    subject.update_last_name(value=LNAME)
    subject.update_email(value=EMAIL)
    subject.update_gender(value=GenderEnum.MALE)

    assert subject.first_name == FNAME
    assert subject.last_name == LNAME
    assert subject.email == EMAIL
    assert subject.gender == GenderEnum.MALE


def test_child_aggregate_update_grade_value_error(child_aggregate):
    subject = child_aggregate
    with pytest.raises(ValueError):
        subject.update_grade(13)

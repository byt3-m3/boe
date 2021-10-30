import pytest
from src.domains.users_domain.services.user_services import (
    PermissionValidationService,
    UserAccount,
    UserManagementService,
    ChildAccount,
)
from src.enums import PermissionsEnum, GenderEnum
from tests.const import (
    TEST_FIRST_NAME,
    TEST_AGE,
    TEST_LAST_NAME
)


def test_permissions_validation_service_validate_permission(admin_role):
    """
    Tests permission is not in role.

    :param admin_role:
    :return:
    """
    test_subject = PermissionValidationService()
    with pytest.raises(PermissionError):
        test_subject.validate_permission(role=admin_role, expected_permission=PermissionsEnum.AccountChangeStatus)


def test_permissions_validation_service_validate_permission_1(admin_role):
    """
    Tests permission is in role.

    :param admin_role:
    :return:
    """
    test_subject = PermissionValidationService()

    test_subject.validate_permission(role=admin_role, expected_permission=PermissionsEnum.ADMIN)


def test_permissions_validation_service_add_permissions_to_role(admin_role):
    """
    Test adding new permission to Role.

    :param admin_role:
    :return:
    """
    test_subject = PermissionValidationService()
    test_subject.add_permissions_to_role(role=admin_role, permissions=[PermissionsEnum.AccountOwner])

    assert PermissionsEnum.AccountOwner in admin_role.permissions


def test_permissions_validation_service_add_permissions_to_role_1(admin_role):
    """
    Test adding new permission to Role when permission is already present in role

    :param admin_role:
    :return:
    """
    test_subject = PermissionValidationService()
    assert len(admin_role.permissions) == 1

    test_subject.add_permissions_to_role(role=admin_role, permissions=[PermissionsEnum.ADMIN])

    assert len(admin_role.permissions) == 1


def test_user_management_service_create_user_account(admin_role):
    service = UserManagementService()
    user = service.create_user_account(
        last_name=TEST_LAST_NAME,
        first_name=TEST_FIRST_NAME,
        roles=[admin_role]
    )

    assert isinstance(user, UserAccount)


def test_user_management_service_create_child_account(admin_role):
    service = UserManagementService()
    user = service.create_child_account(
        last_name=TEST_LAST_NAME,
        first_name=TEST_FIRST_NAME,
        roles=[admin_role],
        age=TEST_AGE,
        gender=GenderEnum.MALE

    )

    assert isinstance(user, ChildAccount)

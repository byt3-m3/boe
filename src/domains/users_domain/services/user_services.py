from typing import List
from uuid import UUID

from cbaxter1988_utils import log_utils
from src.domains.users_domain.factories import (
    UserDomainFactory,
    UserAccount,
    ChildAccount,
    PermissionsEnum,
    GenderEnum,
    Role
)
from src.services.base import Service

domain_factory = UserDomainFactory()

logger = log_utils.get_logger(name=__name__)


class PermissionValidationService(Service):
    @staticmethod
    def validate_permission(role: Role, expected_permission: PermissionsEnum):
        if expected_permission not in role.permissions:
            raise PermissionError(f"{expected_permission} not in role")

    @staticmethod
    def add_permissions_to_role(role: Role, permissions: List[PermissionsEnum]):
        for permission in permissions:
            if permission not in role.permissions:
                logger.debug(f"Added Permission: '{permission}' to Role: {role.name}")
                role.append_permission(permission)
            else:
                logger.debug(f"Permission {permission} already present in Role: {role.name}")


class UserManagementService(Service):
    @staticmethod
    def create_user_account(last_name: str, first_name: str, roles: List[UUID] = None) -> UserAccount:
        return domain_factory.build_user_account(
            last_name=last_name,
            first_name=first_name,
            roles=roles
        )

    @staticmethod
    def create_child_account(last_name: str, first_name: str, age: int, gender: GenderEnum,
                             roles: List[UUID] = None) -> ChildAccount:
        return domain_factory.build_child_account(
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            age=age,
            gender=gender
        )

    @staticmethod
    def create_role(role_name: str, permissions: List[PermissionsEnum]):
        return domain_factory.build_account_role(
            role_name=role_name,
            permissions=permissions
        )

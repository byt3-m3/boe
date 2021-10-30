from typing import List

from src.domains.users_domain.entities.roles import Role
from src.domains.users_domain.entities.users import UserAccount, ChildAccount
from src.enums import PermissionsEnum, GenderEnum


class UserDomainFactory:

    @staticmethod
    def build_user_account(last_name: str, first_name: str, roles: List[Role] = None) -> UserAccount:
        if not roles:
            roles = []

        return UserAccount(
            last_name=last_name,
            first_name=first_name,
            roles=roles
        )

    @staticmethod
    def build_child_account(
            first_name: str,
            last_name: str,
            age: int,
            gender: GenderEnum,
            roles: List[Role] = None,
    ) -> ChildAccount:
        if not roles:
            roles = []

        return ChildAccount(
            first_name=first_name,
            last_name=last_name,
            roles=roles,
            age=age,
            gender=gender,
        )

    @staticmethod
    def build_account_role(role_name: str, permissions: List[PermissionsEnum] = None) -> Role:
        if not permissions:
            permissions = []

        return Role(
            name=role_name,
            permissions=permissions
        )

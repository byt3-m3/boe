from eventsourcing.domain import Aggregate, AggregateEvent
from dataclasses import dataclass
import enum
from typing import Dict, List
from uuid import UUID
from src.enums import PermissionsEnum


class AccountStatusEnum(enum.Enum):
    ACTIVE = 1
    INACTIVE = 2
    OVER_DRAFTED = 3


class TransactionMethodEnum(enum.Enum):
    ADD = 1
    SUBTRACT = 2


@dataclass
class AccountOwner(Aggregate):
    name: str

    class ChangeNameEvent(AggregateEvent):
        value: str


@dataclass
class AccountAdmin(Aggregate):
    name: str
    permissions: List[PermissionsEnum]

    def add_permission(self, permission: PermissionsEnum):
        self.trigger_event(self.AppendPermissionEvent, permission=permission)

    def verify_permission(self, expected_permission) -> bool:
        if expected_permission in self.permissions:
            return True
        else:
            return False

    def verify_permissions(self, expected_permissions: List[PermissionsEnum]) -> bool:
        for permission in expected_permissions:
            if self.verify_permission(expected_permission=permission):
                return True

        return False

    class AppendPermissionEvent(AggregateEvent):
        permission: PermissionsEnum

        def apply(self, aggregate: "AccountAdmin") -> None:
            aggregate.permissions.append(self.permission)

    class DeletePermissionEvent(AggregateEvent):
        permission_id: UUID


@dataclass
class AccountAggregate(Aggregate):
    balance: float
    owner: AccountOwner
    status: AccountStatusEnum = AccountStatusEnum.ACTIVE
    admin_map: Dict[UUID, AccountAdmin] = dict

    def verify_admin(self, expected_admin: AccountAdmin):
        if expected_admin.id in self.admin_map:
            return True
        else:
            return False

    def change_balance(self, method: TransactionMethodEnum, value: float, admin: AccountAdmin):
        self.trigger_event(
            self.ChangeAccountBalanceEvent,
            transaction_method=TransactionMethodEnum(method),
            new_value=value,
            admin=admin,
        )

    def change_status(self, status: AccountStatusEnum, admin: AccountAdmin):
        self.trigger_event(
            self.ChangeAccountStatusEvent,
            status=status,
            admin=admin
        )

    def add_account_admin(self, requesting_admin, admin: AccountAdmin):
        self.trigger_event(
            self.AddAccountAdminEvent,
            requesting_admin=requesting_admin,
            new_admin=admin
        )

    @staticmethod
    def validate_aggregate_admin(aggregate: "AccountAggregate", expected_admin: AccountAdmin):
        if not aggregate.verify_admin(expected_admin=expected_admin):
            raise PermissionError(f"Admin:'{expected_admin.name}' not associated with this account")

    class ChangeAccountBalanceEvent(AggregateEvent):
        transaction_method: TransactionMethodEnum
        new_value: float
        admin: AccountAdmin
        permissions = [PermissionsEnum.ADMIN, PermissionsEnum.ChangeAccountBalance]

        def apply(self, aggregate: 'AccountAggregate') -> None:
            AccountAggregate.validate_aggregate_admin(aggregate=aggregate, expected_admin=self.admin)

            if self.admin.verify_permissions(expected_permissions=self.permissions):
                if self.transaction_method == TransactionMethodEnum.ADD:
                    aggregate.balance += self.new_value

                if self.transaction_method == TransactionMethodEnum.SUBTRACT:
                    aggregate.balance -= self.new_value

    class ChangeAccountStatusEvent(AggregateEvent):
        admin: AccountAdmin
        status: AccountStatusEnum
        permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.ChangeAccountStatus
        ]

        def apply(self, aggregate: 'AccountAggregate') -> None:
            AccountAggregate.validate_aggregate_admin(aggregate=aggregate, expected_admin=self.admin)

            permission_check = self.admin.verify_permissions(expected_permissions=self.permissions)

            if permission_check:
                aggregate.status = self.status

    class AddAccountAdminEvent(AggregateEvent):
        requesting_admin: AccountAdmin
        new_admin: AccountAdmin

        def apply(self, aggregate: "AccountAggregate") -> None:
            aggregate.admin_map[self.new_admin.id] = self.new_admin

    class RemoveAccountAdminEvent(AggregateEvent):
        admin: AccountAdmin
        admin_id: UUID

    class SetAccountOwnerEvent(AggregateEvent):
        admin: AccountAdmin
        owner: AccountOwner


def test():
    liam = AccountOwner(name="Liam")
    elijah = AccountOwner(name="Elijah")
    minh = AccountAdmin(name="Minh", permissions=[PermissionsEnum.ADMIN])
    courtney = AccountAdmin(name="Courtney", permissions=[PermissionsEnum.ADMIN])

    liam_account = AccountAggregate(balance=100, owner=liam, admin_map={minh.id: minh})
    elijah_account = AccountAggregate(balance=200, owner=liam, admin_map={courtney.id: courtney})

    # print(liam_account.admin_map)
    print(liam_account.status)
    liam_account.change_balance(method=TransactionMethodEnum.ADD, value=10, admin=minh)
    elijah_account.change_balance(method=TransactionMethodEnum.ADD, value=30, admin=courtney)
    liam_account.change_status(status=AccountStatusEnum.INACTIVE, admin=minh)
    # print(liam_account.pending_events)
    from pprint import pprint

    print(liam_account.status)


test()

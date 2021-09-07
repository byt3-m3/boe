import enum
from dataclasses import dataclass
from typing import Dict, List, Any
from uuid import UUID

from eventsourcing.domain import Aggregate, AggregateEvent
from src.domains.core_domain import CoreAggregate
from src.enums import PermissionsEnum
from src.utils.aggregate_utils import verify_aggregate_permissions
from src.models.user_models import PermissionsEnum


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
class AccountAdmin(CoreAggregate):
    model: ParentModel
    permissions: List[PermissionsEnum]

    def append_permissions(self: "AccountAdmin", permissions: List[PermissionsEnum]):
        for p in permissions:
            if isinstance(p, PermissionsEnum):
                self.append_permission(permission=p)

    def append_permission(self, permission: PermissionsEnum):
        self.trigger_event(self.AppendPermissionEvent, permission=permission)

    def remove_permission(self, permission: PermissionsEnum):
        self.trigger_event(self.RemovePermissionEvent, permission=permission)

    class AppendPermissionEvent(AggregateEvent):
        permission: PermissionsEnum
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountAdminModifyPermissions
        ]

        def apply(self, aggregate: "AccountAdmin") -> None:
            aggregate.permissions.append(self.permission)

    class RemovePermissionEvent(AggregateEvent):
        permission: PermissionsEnum

        def apply(self, aggregate: "AccountAdmin") -> None:
            aggregate.permissions.remove(self.permission)


@dataclass
class BankAccount(CoreAggregate):
    balance: float
    owner: AccountOwner
    admin_map: Dict[UUID, AccountAdmin]
    status: AccountStatusEnum = AccountStatusEnum.ACTIVE
    is_overdrafted: bool = False
    overdraft_protection: bool = False


    def verify_admin(self, expected_admin: AccountAdmin) -> bool:
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

    def add_account_admin(self, requesting_admin: AccountAdmin, new_admin: AccountAdmin):
        self.trigger_event(
            self.AddAccountAdminEvent,
            requesting_admin=requesting_admin,
            new_admin=new_admin
        )

    def delete_account_admin(self, admin, target_id: UUID):
        self.trigger_event(
            self.DeleteAccountAdminEvent,
            admin=admin,
            target_id=target_id

        )
        pass

    def enable_overdraft_protection(self, admin: AccountAdmin):
        self.trigger_event(self.EnableOverDraftProtectionEvent, admin=admin)

    def disable_overdraft_protection(self, admin: AccountAdmin):
        self.trigger_event(self.DisableOverDraftProtectionEvent, admin=admin)

    def validate_admin(self, expected_admin: AccountAdmin):
        if not self.verify_admin(expected_admin=expected_admin):
            msg = f"Admin:'{expected_admin.name}' not associated with this account"
            self.trigger_event(self.PermissionEvent, context='msg')
            raise PermissionError(msg)

    def check_overdraft(self, method: TransactionMethodEnum, value: float, admin: AccountAdmin) -> (bool, float):
        future_balance = 0
        if method == TransactionMethodEnum.ADD:
            future_balance = self.balance + value

        if method == TransactionMethodEnum.SUBTRACT:
            future_balance = self.balance - value

        if future_balance < 0:
            return True, future_balance

        else:
            return False, future_balance

    class AccountOverdraftedEvent(AggregateEvent):
        context: Any
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountSetOverdraft
        ]

        def apply(self, aggregate: 'BankAccount') -> None:
            aggregate.is_overdrafted = True

    class ClearOverDraftEvent(AggregateEvent):
        admin: AccountAdmin
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountClearOverDraft
        ]

        def apply(self, aggregate: 'BankAccount') -> None:
            aggregate.validate_admin(expected_admin=self.admin)
            if verify_aggregate_permissions(aggergate=self.admin, expected_permissions=self._permissions):
                aggregate.is_overdrafted = False

    class ChangeAccountBalanceEvent(AggregateEvent):
        transaction_method: TransactionMethodEnum
        new_value: float
        admin: AccountAdmin
        _permissions = [PermissionsEnum.ADMIN, PermissionsEnum.AccountChangeBalance]

        def apply(self, aggregate: 'BankAccount') -> None:
            aggregate.validate_admin(expected_admin=self.admin)

            if verify_aggregate_permissions(aggergate=self.admin, expected_permissions=self._permissions):
                overdrafted, future_balance = aggregate.check_overdraft(
                    method=self.transaction_method,
                    value=self.new_value,
                    admin=self.admin
                )
                if aggregate.overdraft_protection:
                    if overdrafted:
                        aggregate.trigger_event(
                            aggregate.OverDraftProtectionEvent,
                            context=f'Prorected from Potential Overdraft: "{future_balance}"',
                        )
                        return

                if self.transaction_method == TransactionMethodEnum.ADD:
                    aggregate.balance += self.new_value

                if self.transaction_method == TransactionMethodEnum.SUBTRACT:
                    aggregate.balance -= self.new_value

                    if aggregate.balance < 0:
                        aggregate.trigger_event(
                            aggregate.AccountOverdraftedEvent,
                            context=f'Account Overdrafted: "{future_balance}"',
                        )

    class ChangeAccountStatusEvent(AggregateEvent):
        admin: AccountAdmin
        status: AccountStatusEnum
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountChangeStatus
        ]

        def apply(self, aggregate: 'BankAccount') -> None:
            aggregate.validate_admin(expected_admin=self.admin)
            if verify_aggregate_permissions(aggregate=self.admin, expected_permissions=self._permissions):
                aggregate.status = self.status

    class AddAccountAdminEvent(AggregateEvent):
        requesting_admin: AccountAdmin
        new_admin: AccountAdmin

        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountAddAccountAdmin
        ]

        def apply(self, aggregate: "BankAccount") -> None:
            aggregate.validate_admin(expected_admin=self.requesting_admin)
            if verify_aggregate_permissions(aggergate=self.requesting_admin, expected_permissions=self._permissions):
                aggregate.admin_map[self.new_admin.id] = self.new_admin

    class DeleteAccountAdminEvent(AggregateEvent):
        admin: AccountAdmin
        target_id: UUID
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountDeleteAccountAdmin
        ]

        def apply(self, aggregate: 'BankAccount') -> None:
            aggregate.validate_admin(expected_admin=self.admin)
            if verify_aggregate_permissions(aggergate=self.admin, expected_permissions=self._permissions):
                aggregate.admin_map.pop(self.target_id)

    class SetAccountOwnerEvent(AggregateEvent):
        admin: AccountAdmin
        owner: AccountOwner

    class EnableOverDraftProtectionEvent(AggregateEvent):
        admin: AccountAdmin
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountModifyOverdraftProtection
        ]

        def apply(self, aggregate: 'BankAccount') -> None:
            if verify_aggregate_permissions(aggregate=self.admin, expected_permissions=self._permissions):
                aggregate.overdraft_protection = True

    class DisableOverDraftProtectionEvent(AggregateEvent):
        admin: AccountAdmin
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountModifyOverdraftProtection
        ]

        def apply(self, aggregate: 'BankAccount') -> None:
            if verify_aggregate_permissions(aggergate=self.admin, expected_permissions=self._permissions):
                aggregate.overdraft_protection = False

    class OverDraftProtectionEvent(AggregateEvent):
        context: Any

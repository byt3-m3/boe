from dataclasses import dataclass
from typing import List, Any
from uuid import UUID

from eventsourcing.domain import Aggregate, AggregateEvent, event
from src.domains.core_domain import CoreAggregate
from src.domains.user_domain import RoleAggregate
from src.enums import AccountStatusEnum, TransactionMethodEnum
from src.models.bank_models import BankAccountDataModel
from src.models.user_models import PermissionsEnum
from src.roles import system_role
from src.utils.aggregate_utils import verify_aggregate_permissions


@dataclass
class AccountOwner(Aggregate):
    name: str

    class ChangeNameEvent(AggregateEvent):
        value: str


@dataclass
class AccountAdmin(CoreAggregate):
    role: RoleAggregate


@dataclass
class BankAccount(CoreAggregate):
    model: BankAccountDataModel

    status: AccountStatusEnum = AccountStatusEnum.ACTIVE
    is_overdrafted: bool = False
    overdraft_protection: bool = False

    def _check_overdraft(self, method: TransactionMethodEnum, value: float, role: RoleAggregate) -> (bool, float):
        future_balance = 0
        if method == TransactionMethodEnum.ADD:
            future_balance = self.model.balance + value

        if method == TransactionMethodEnum.SUBTRACT:
            future_balance = self.model.balance - value

        if future_balance < 0:
            return True, future_balance

        else:
            return False, future_balance

    @staticmethod
    def _verify_role_permissions(role: RoleAggregate, expected_permissions: List[PermissionsEnum]) -> bool:

        def filter_permissions(permission):
            for p in role.permissions:
                if p == permission:
                    return True
                else:
                    return False

        filtered_permissions = list(filter(filter_permissions, expected_permissions))
        if len(filtered_permissions) > 0:
            return True
        else:
            return False

    def verify_admin(self, expected_admin: AccountAdmin) -> bool:
        # TODO: Remove Once Vents are convereted
        if expected_admin.id in self.admin_map:
            return True
        else:
            return False

    @event("ChangeBalance")
    def change_balance(self, method: TransactionMethodEnum, value: float, role: RoleAggregate):
        if self._verify_role_permissions(
                role=role,
                expected_permissions=[
                    PermissionsEnum.ADMIN,
                    PermissionsEnum.AccountChangeBalance
                ]
        ):
            overdrafted, future_balance = self._check_overdraft(
                method=method,
                value=value,
                role=role
            )
            if self.overdraft_protection:
                if overdrafted:
                    self.trigger_event(
                        self.OverDraftProtectionEvent,
                        context=f'Protected from Potential Overdraft: "{future_balance}"',
                    )
                    return

            if method == TransactionMethodEnum.ADD:
                self.model.balance += value

            if method == TransactionMethodEnum.SUBTRACT:
                self.model.balance -= value

                if self.model.balance < 0:
                    self.trigger_overdraft(status=True, role=system_role)

    @event("ChangeStatus")
    def change_status(self, status: AccountStatusEnum, role: RoleAggregate):
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountChangeStatus
        ]
        if self._verify_role_permissions(role=role, expected_permissions=_permissions):
            self.status = status

    @event("EnableOverDraftProtection")
    def enable_overdraft_protection(self, role: RoleAggregate):
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountModifyOverdraftProtection
        ]
        if self._verify_role_permissions(role=role, expected_permissions=_permissions):
            self.overdraft_protection = True

    @event("DisableOverDraftProtection")
    def disable_overdraft_protection(self, role: RoleAggregate):
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountModifyOverdraftProtection
        ]
        if self._verify_role_permissions(role=role, expected_permissions=_permissions):
            self.overdraft_protection = False

    @event("TriggerOverDraft")
    def trigger_overdraft(self, status: bool, role: RoleAggregate):
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountSetOverdraft
        ]
        if self._verify_role_permissions(role=role, expected_permissions=_permissions):
            self.is_overdrafted = status

    def validate_admin(self, expected_admin: AccountAdmin):
        if not self.verify_admin(expected_admin=expected_admin):
            msg = f"Admin:'{expected_admin.name}' not associated with this account"
            self.trigger_event(self.PermissionEvent, context='msg')
            raise PermissionError(msg)

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

    class OverDraftProtectionEvent(AggregateEvent):
        context: Any

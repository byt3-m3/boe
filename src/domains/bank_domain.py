from dataclasses import dataclass
from typing import List, Any

from eventsourcing.domain import Aggregate, AggregateEvent, event
from src.domains.core_domain import CoreAggregate
from src.domains.user_domain import RoleAggregate
from src.enums import AccountStatusEnum, TransactionMethodEnum
from src.models.bank_models import BankAccountDataModel
from src.models.user_models import PermissionsEnum, ChildDataModel, AdultDataModel
from src.roles import system_role


@dataclass
class AccountOwner(Aggregate):
    model: ChildDataModel

    class ChangeNameEvent(AggregateEvent):
        value: str


class AccountAdmin(Aggregate):
    model: AdultDataModel
    role: RoleAggregate


@dataclass
class BankAccount(CoreAggregate):
    model: BankAccountDataModel
    owner: AccountOwner
    # status: AccountStatusEnum = AccountStatusEnum.ACTIVE
    # is_overdrafted: bool = False
    # overdraft_protection: bool = False

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
            if self.model.overdraft_protection:
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
            self.model.status = status

    @event("EnableOverDraftProtection")
    def enable_overdraft_protection(self, role: RoleAggregate):
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountModifyOverdraftProtection
        ]
        if self._verify_role_permissions(role=role, expected_permissions=_permissions):
            self.model.overdraft_protection = True

    @event("DisableOverDraftProtection")
    def disable_overdraft_protection(self, role: RoleAggregate):
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountModifyOverdraftProtection
        ]
        if self._verify_role_permissions(role=role, expected_permissions=_permissions):
            self.model.overdraft_protection = False

    @event("TriggerOverDraft")
    def trigger_overdraft(self, status: bool, role: RoleAggregate):
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountSetOverdraft
        ]
        if self._verify_role_permissions(role=role, expected_permissions=_permissions):
            self.model.is_overdrafted = status

    class AccountOverdraftedEvent(AggregateEvent):
        context: Any
        _permissions = [
            PermissionsEnum.ADMIN,
            PermissionsEnum.AccountSetOverdraft
        ]

        def apply(self, aggregate: 'BankAccount') -> None:
            aggregate.is_overdrafted = True

    class OverDraftProtectionEvent(AggregateEvent):
        context: Any

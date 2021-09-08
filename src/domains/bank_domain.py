from dataclasses import dataclass, field
from typing import List, Any
from uuid import UUID

from eventsourcing.domain import AggregateEvent, event
from src.domains.core_domain import CoreAggregate
from src.domains.user_domain import RoleAggregate, ChildAggregate, AdultAggregate
from src.enums import AccountStatusEnum, TransactionMethodEnum, PermissionsEnum
from src.roles import system_role


@dataclass
class BankAccount(CoreAggregate):
    balance: float
    owner: UUID = field(default=None)
    admin: UUID = field(default=None)
    status: AccountStatusEnum = AccountStatusEnum.ACTIVE
    is_overdrafted: bool = False
    overdraft_protection: bool = False

    def _check_overdraft(self, method: TransactionMethodEnum, value: float) -> (bool, float):
        future_balance = 0
        if method == TransactionMethodEnum.ADD:
            future_balance = self.balance + value

        if method == TransactionMethodEnum.SUBTRACT:
            future_balance = self.balance - value

        if future_balance < 0:
            return True, future_balance

        else:
            return False, future_balance

    @staticmethod
    def _verify_role_permissions(roles: RoleAggregate, expected_permissions: List[PermissionsEnum]) -> bool:
        def filter_permissions(permission):
            for _role in roles:
                for p in _role.permissions:
                    if p == permission:
                        return True
                    else:
                        return False

        filtered_permissions = list(filter(filter_permissions, expected_permissions))
        if len(filtered_permissions) > 0:
            return True
        else:
            return False

    @event("UpdateAdmin")
    def update_admin(self, adult_aggregate: AdultAggregate):
        self.admin = adult_aggregate.id

    @event("UpdateOwner")
    def update_owner(self, child_aggregate: ChildAggregate):
        self.owner = child_aggregate.id

    @event("ChangeBalance")
    def change_balance(self, method: TransactionMethodEnum, value: float):

        overdrafted, future_balance = self._check_overdraft(
            method=method,
            value=value,
        )
        if self.overdraft_protection:
            if overdrafted:
                self.trigger_event(
                    self.OverDraftProtectionEvent,
                    context=f'Protected from Potential Overdraft: "{future_balance}"',
                )
                return

        if method == TransactionMethodEnum.ADD:
            self.balance += value

        if method == TransactionMethodEnum.SUBTRACT:
            self.balance -= value

            if self.balance < 0:
                self.trigger_overdraft(status=True)

    @event("ChangeStatus")
    def change_status(self, status: AccountStatusEnum):
        self.status = status

    @event("EnableOverDraftProtection")
    def enable_overdraft_protection(self):

        self.overdraft_protection = True

    @event("DisableOverDraftProtection")
    def disable_overdraft_protection(self):

        self.overdraft_protection = False

    @event("TriggerOverDraft")
    def trigger_overdraft(self, status: bool):

        self.is_overdrafted = status

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

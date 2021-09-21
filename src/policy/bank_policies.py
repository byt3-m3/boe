from typing import List

from src.domains.bank_domain import BankAccount, TransactionMethodEnum, RoleAggregate, PermissionsEnum
from src.policy import Policy
from src.utils.aggregate_utils import verify_role_permissions


class AccountOverdraftCheckPolicy(Policy):
    def __init__(
            self,
            bank_accout: BankAccount,
            new_amount: float,
            roles: List[RoleAggregate],
            expected_permissions: List[PermissionsEnum],
            method: TransactionMethodEnum
    ):
        self.bank_account = bank_accout
        self.new_amount = new_amount
        self.roles = roles
        self.expected_permissions = expected_permissions
        self.method = method

    def evaluate(self) -> bool:
        future_balance = 0
        if verify_role_permissions(expected_permissions=self.expected_permissions, roles=self.roles):
            if self.method == TransactionMethodEnum.ADD:
                future_balance = self.bank_account.balance + self.new_amount

            if self.method == TransactionMethodEnum.SUBTRACT:
                future_balance = self.bank_account.balance - self.new_amount

            if future_balance < 0:
                return True

            else:
                return False

        else:
            raise PermissionError("Role Contains Invalid Permissions")
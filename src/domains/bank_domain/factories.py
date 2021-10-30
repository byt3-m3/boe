from src.domains.bank_domain.entities.bank_account import BankAccount
from src.domains.bank_domain.value_objects.transaction import Transaction, TransactionMethodEnum

from  uuid import UUID

class BankDomainFactory:

    @staticmethod
    def build_transaction(value: float, method: TransactionMethodEnum) -> Transaction:
        """
        Builds Transaction ValueObject

        :param value:
        :param method:
        :return:
        """
        return Transaction(
            method=method,
            value=value
        )

    @staticmethod
    def build_bank_account(owner_id: UUID, overdraft_protection=False, balance=0) -> BankAccount:
        """
        Builds Bank Account entity

        :param owner_id:
        :param overdraft_protection:
        :param balance:
        :return:
        """
        return BankAccount.create(
            overdraft_protection=overdraft_protection,
            balance=balance,
            owner_id=owner_id
        )

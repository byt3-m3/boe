from uuid import UUID

from cbaxter1988_utils import log_utils
from src.domains.bank_domain.entities.bank_account import BankAccount
from src.domains.bank_domain.factories import BankDomainFactory
from src.domains.bank_domain.value_objects.transaction import Transaction
from src.enums import TransactionMethodEnum, BankAccountStateEnum
from src.services.base import Service

logger = log_utils.get_logger(__name__)
domain_factory = BankDomainFactory()


class TransactionValidationService(Service):
    """
    Preforms validations for transactions.

    """

    @staticmethod
    def verify_transaction(
            account: BankAccount,
            transaction: Transaction
    ) -> bool:
        """
        Validates account transation. Returns False if Account is under Zero balance.

        :param account:
        :param transaction:
        :return:
        """
        future_balance = 0
        if transaction.method == TransactionMethodEnum.ADD:
            future_balance = account.balance + transaction.value
        #
        if transaction.method == TransactionMethodEnum.SUBTRACT:
            future_balance = account.balance - transaction.value
        #
        if future_balance < 0:
            return False

        else:
            return True


class AccountManagementService(Service):

    @staticmethod
    def create_account(owner_id: UUID, overdraft_protection: bool) -> BankAccount:
        _account = domain_factory.build_bank_account(
            balance=0,
            owner_id=owner_id,
            overdraft_protection=overdraft_protection,

        )
        return _account

    @staticmethod
    def process_transaction(account: BankAccount, transaction: Transaction):
        verification_result = TransactionValidationService.verify_transaction(
            account=account,
            transaction=transaction
        )
        if verification_result is True:
            if account.state != BankAccountStateEnum.OVER_DRAFTED:
                account.apply_transaction(transaction=transaction)

        if verification_result is False:
            if account.is_overdrafted:
                logger.info(f"Unable to process transaction {transaction} - {account.id} is overdrafted")
                return

            logger.info(f"Transaction {transaction} failed verification")
            if account.overdraft_protection:
                logger.info(f"Overdraft Protection detected on account: {account.id}")
                logger.info(f"Unable to process transaction {transaction} - {account.id}")

            else:
                account.apply_transaction(transaction=transaction)
                if account.balance < 0:
                    account.set_state(state=BankAccountStateEnum.OVER_DRAFTED)

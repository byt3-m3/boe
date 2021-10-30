from dataclasses import dataclass, field
from uuid import UUID

from eventsourcing.domain import Aggregate, event
from src.domains.bank_domain.value_objects.transaction import Transaction
from src.enums import BankAccountStateEnum, TransactionMethodEnum
from src.utils.core_utils import make_id


@dataclass
class BankAccount(Aggregate):
    balance: float
    owner_id: UUID
    admin_id: UUID = field(default=None)
    state: BankAccountStateEnum = BankAccountStateEnum.OPEN
    is_overdrafted: bool = False
    overdraft_protection: bool = False

    def serialize(self):
        return {
            "balance": self.balance,
            "owner_id": self.owner_id,
            "admin_id": self.admin_id,
            "status": self.state.value,
            "is_overdrafted": self.is_overdrafted,
            "overdraft_protection": self.overdraft_protection,
        }

    @classmethod
    def create(cls, balance: float, owner_id: UUID, admin_id: UUID = None, overdraft_protection: bool = False):
        return cls._create(
            cls.Created,
            id=cls.create_id(owner_id=owner_id),
            balance=balance,
            owner_id=owner_id,
            admin_id=admin_id,
            overdraft_protection=overdraft_protection,
            state=BankAccountStateEnum.OPEN,
            is_overdrafted=False
        )

    @classmethod
    def create_id(cls, owner_id):
        return make_id(domain="bank_account", key=owner_id)

    @event
    def set_state(self, state: BankAccountStateEnum):
        if state.OVER_DRAFTED:
            self.is_overdrafted = True

        self.state = state

    @event
    def apply_transaction(self, transaction: Transaction):
        if transaction.method == TransactionMethodEnum.ADD:
            self.balance += transaction.value

        if transaction.method == TransactionMethodEnum.SUBTRACT:
            self.balance -= transaction.value

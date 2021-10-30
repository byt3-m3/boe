from dataclasses import dataclass

from src.enums import TransactionMethodEnum


@dataclass(frozen=True)
class Transaction:
    method: TransactionMethodEnum
    value: float

    def __repr__(self):
        return f"<Transaction(method={self.method}, value={self.value})>"
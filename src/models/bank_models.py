from dataclasses import dataclass
from src.enums import AccountStatusEnum

@dataclass
class BankAccountDataModel:
    balance: float
    status: AccountStatusEnum = AccountStatusEnum.ACTIVE
    is_overdrafted: bool = False
    overdraft_protection: bool = False
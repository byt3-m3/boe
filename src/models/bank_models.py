from dataclasses import dataclass, field
from typing import List
from src.enums import PermissionsEnum, AccountStatusEnum


@dataclass
class AccountOwnerDataModel:
    pass

@dataclass
class AccountAdminDataModel:
    pass


@dataclass
class BankAccountDataModel:
    balance: float
    owner: AccountOwnerDataModel

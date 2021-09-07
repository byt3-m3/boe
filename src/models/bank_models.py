from dataclasses import dataclass




@dataclass
class BankAccountDataModel:
    balance: float
    owner: AccountOwnerDataModel

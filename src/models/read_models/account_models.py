from src.models.read_models import ReadModel
from dataclasses import dataclass
from src.enums import AccountStatusEnum

@dataclass(frozen=True)
class AccountReadModel:
    balance: float
    status: AccountStatusEnum

    @staticmethod
    def encode(data):
        return AccountReadModel(
            balance=data.get("balance"),
            status=AccountStatusEnum(data.get("status")),
            is_overdrafted=data.get("is_overdrafted"),
            overdraft_protection=data.get("overdraft_protection"),

        )
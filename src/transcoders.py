from dataclasses import dataclass, asdict
from eventsourcing.persistence import Transcoding
from src.models.user_models import ChildDataModel
from src.models.bank_models import BankAccountDataModel
from src.domains.user_domain import RoleAggregate
from src.enums import GenderEnum, AccountStatusEnum, PermissionsEnum

class ChildDataModelTranscoding(Transcoding):
    type = ChildDataModel
    name = "model"

    def encode(self, o: ChildDataModel) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return ChildDataModel(**d)

class RoleAggregateTranscoding(Transcoding):
    type = RoleAggregate
    name = "role"

    def encode(self, o: RoleAggregate) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return RoleAggregate(**d)


class BankAccountDataModelTranscoding(Transcoding):
    type = BankAccountDataModel
    name = "model"

    def encode(self, o: BankAccountDataModel) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return BankAccountDataModel(**d)


class GenderEnumTranscoding(Transcoding):
    type = GenderEnum
    name = "gender"

    def encode(self, o: GenderEnum) -> int:
        return o.value

    def decode(self, d: int):
        return GenderEnum(d)

class AccountStatusEnumTranscoding(Transcoding):
    type = AccountStatusEnum
    name = "status"

    def encode(self, o: AccountStatusEnum) -> int:
        return o.value

    def decode(self, d: int):
        return AccountStatusEnum(d)

class PermissionsEnumTranscoding(Transcoding):
    type = PermissionsEnum
    name = "permissions_enum"

    def encode(self, o: PermissionsEnum) -> int:
        return o.value

    def decode(self, d: int):
        return PermissionsEnum(d)
import json

from eventsourcing.persistence import Transcoding
from src.enums import (
    GenderEnum,
    AccountStatusEnum,
    PermissionsEnum,
    TransactionMethodEnum,
    TaskState, BankAccountStateEnum
)


class TaskStateTranscoding(Transcoding):
    type = TaskState
    name = "TaskState"

    def encode(self, o: TaskState) -> int:
        return o.value

    def decode(self, d: int):
        return TaskState(d)


class BankAccountStateTranscoding(Transcoding):
    type = BankAccountStateEnum
    name = "BankAccountStateEnum"

    def encode(self, o: BankAccountStateEnum) -> int:
        return o.value

    def decode(self, d: int):
        return BankAccountStateEnum(d)


class GenderEnumTranscoding(Transcoding):
    type = GenderEnum
    name = "gender"

    def encode(self, o: GenderEnum) -> int:
        return o.value

    def decode(self, d: int):
        return GenderEnum(d)


class TransactionMethodEnumTranscoding(Transcoding):
    type = TransactionMethodEnum
    name = "transaction_method"

    def encode(self, o: TransactionMethodEnum) -> int:
        return o.value

    def decode(self, d: int):
        return TransactionMethodEnum(d)


class AccountStatusEnumTranscoding(Transcoding):
    type = AccountStatusEnum
    name = "status"

    def encode(self, o: AccountStatusEnum) -> int:
        return o.value

    def decode(self, d: int):
        return AccountStatusEnum(d)


class BytesTranscoding(Transcoding):
    type = bytes
    name = "bytes"

    def encode(self, o: bytes) -> str:
        return json.loads(o)

    def decode(self, d: int):
        return json.dumps(d)


class PermissionsEnumTranscoding(Transcoding):
    type = PermissionsEnum
    name = "permissions_enum"

    def encode(self, o: PermissionsEnum) -> int:
        return o.value

    def decode(self, d: int):
        return PermissionsEnum(d)

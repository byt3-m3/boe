from dataclasses import asdict

from eventsourcing.persistence import Transcoding
from src.domains.user_domain import RoleAggregate
from src.enums import GenderEnum, AccountStatusEnum, PermissionsEnum
import json


class RoleAggregateTranscoding(Transcoding):
    type = RoleAggregate
    name = "role"

    def encode(self, o: RoleAggregate) -> str:
        return asdict(o)

    def decode(self, d: dict):
        return RoleAggregate(**d)


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

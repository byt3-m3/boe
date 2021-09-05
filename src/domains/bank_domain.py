from eventsourcing.domain import Aggregate, AggregateEvent
from dataclasses import dataclass
import enum
from typing import Dict, List
from uuid import UUID


class AccountStatusEnum(enum.Enum):
    ACTIVE = 1
    INACTIVE = 1
    OVER_DRAFTED = 1


class PermissionsEnum(enum.Enum):
    ADMIN = 0
    ChangeBalance = 1


class TransactionMethodEnum(enum.Enum):
    ADD = 1
    SUBTRACT = 2


@dataclass
class AccountOwner(Aggregate):
    name: str

    class ChangeNameEvent(AggregateEvent):
        value: str


@dataclass
class AccountAdmin(Aggregate):
    name: str
    permissions: List[PermissionsEnum]

    class AddPermissionEvent(AggregateEvent):
        permission: PermissionsEnum

        def apply(self, aggregate: "AccountAdmin") -> None:
            aggregate.permissions.append(self.permission)

    class DeletePermissionEvent(AggregateEvent):
        permission_id: UUID


@dataclass
class AccountAggregate(Aggregate):
    balance: float
    owner: AccountOwner
    status: AccountStatusEnum = AccountStatusEnum.ACTIVE
    admin_map: Dict[UUID, AccountAdmin] = dict

    def change_balance(self, method: TransactionMethodEnum, value: float, admin: AccountAdmin):
        self.trigger_event(
            self.ChangeAccountBalanceEvent,
            transaction_method=TransactionMethodEnum(method),
            new_value=value,
            admin=admin,
        )

    def add_account_admin(self, requesting_admin, admin: AccountAdmin):
        self.trigger_event(
            self.AddAccountAdminEvent,
            requesting_admin=requesting_admin,
            new_admin=admin
        )

    class ChangeAccountBalanceEvent(AggregateEvent):
        transaction_method: TransactionMethodEnum
        new_value: float
        admin: AccountAdmin

        def apply(self, aggregate: 'AccountAggregate') -> None:
            if not aggregate.admin_map.get(self.admin.id):
                raise Exception("Admin not associated with this account")

            if PermissionsEnum.ChangeBalance in self.admin.permissions or PermissionsEnum.ADMIN in self.admin.permissions:

                if self.transaction_method == TransactionMethodEnum.ADD:
                    aggregate.balance += self.new_value

                if self.transaction_method == TransactionMethodEnum.SUBTRACT:
                    aggregate.balance -= self.new_value

    class ChangeAccountStatusEvent(AggregateEvent):
        admin: AccountAdmin
        status: AccountStatusEnum

    class AddAccountAdminEvent(AggregateEvent):
        requesting_admin: AccountAdmin
        new_admin: AccountAdmin

        def apply(self, aggregate: "AccountAggregate") -> None:
            aggregate.admin_map[self.new_admin.id] = self.new_admin

    class RemoveAccountAdminEvent(AggregateEvent):
        admin: AccountAdmin
        admin_id: UUID

    class SetAccountOwnerEvent(AggregateEvent):
        admin: AccountAdmin
        owner: AccountOwner

    class SetAccountClosedEvent(AggregateEvent):
        pass


def test():
    liam = AccountOwner(name="Liam")
    elijah = AccountOwner(name="Elijah")
    minh = AccountAdmin(name="Minh", permissions=[PermissionsEnum.ADMIN])
    me = AccountAdmin(name="Minh", permissions=[PermissionsEnum.ADMIN])

    liam_account = AccountAggregate(balance=100, owner=liam, admin_map={minh.id: minh})
    elijah_account = AccountAggregate(balance=200, owner=liam, admin_map={minh.id: minh})

    # print(liam_account.admin_map)

    liam_account.change_balance(method=TransactionMethodEnum.ADD, value=10, admin=minh)
    elijah_account.change_balance(method=TransactionMethodEnum.ADD, value=30, admin=minh)
    print(liam_account.pending_events)
    print(elijah_account.pending_events)
    print(liam_account.balance, elijah_account.balance)


test()

from dataclasses import asdict, is_dataclass
from typing import List
from uuid import UUID

import pymongo.errors
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder, InfrastructureFactory
from src.const import IN_PRODUCTION
from src.data_access.query_table_dao import QueryTableDAO
from src.domains.bank_domain import (
    BankAccount,

)
from src.domains.task_domain import (
    TaskAggregate
)
from src.domains.user_domain import (
    ChildAggregate,
    RoleAggregate,
    AdultAggregate
)
from src.domains.user_domain import (
    UserAccountAggregate
)
from src.enums import (
    GenderEnum,
    PermissionsEnum,
    AccountStatusEnum,
    TransactionMethodEnum
)
from src.transcoders import (
    PermissionsEnumTranscoding,
    AccountStatusEnumTranscoding,
    GenderEnumTranscoding,
    RoleAggregateTranscoding,
    TransactionMethodEnumTranscoding
)
from src.utils.aggregate_utils import verify_role_permissions, extract_type

query_table_dao = QueryTableDAO(db_host="192.168.1.5", db_port=27017, db_name="BOE")


class BOEApplication(Application):

    # def __init__(self):
    #     super().__init__()

    # self.events.recorder = MongoRecorder(db_host='192.168.1.5', db_port=27017)

    def setup(self):
        admin_role_id = self.create_role(name='AdminRole', permissions=[PermissionsEnum.ADMIN])
        child_role_id = self.create_role(name='ChildRole', permissions=[PermissionsEnum.Child])
        return admin_role_id, child_role_id

    @staticmethod
    def save_aggregate_to_query_table(aggregate, table_id, **kwargs):
        if is_dataclass(aggregate):

            try:
                query_table_dao.add_aggregate(
                    _type=extract_type(aggregate),
                    _version=aggregate.version,
                    _id=aggregate.id,
                    collection=table_id,
                    **aggregate.serialize()
                )

                return True

            except pymongo.errors.DuplicateKeyError:
                query_table_dao.update_aggregate(
                    _type=extract_type(aggregate),
                    _version=aggregate.version,
                    _id=aggregate.id,
                    collection=table_id,
                    **aggregate.serialize()
                )

    def construct_factory(self) -> InfrastructureFactory:
        if IN_PRODUCTION:
            print("Using SQL Lite DB")
            return Factory.construct(self.__class__.__name__, env=self.env)
        else:
            print("Using Default DB")
            return InfrastructureFactory.construct(self.__class__.__name__, env=self.env)

    def _validate_items_type(self, items, expected_type, ) -> bool:
        assert False not in [
            isinstance(item, expected_type) for item in items
        ]
        return True

    def _get_aggregate(self, aggregate_id: UUID, version=None):
        return self.repository.get(aggregate_id)

    def _get_roles_from_account_aggregate(self, account_admin: UserAccountAggregate):
        role_ids = [role for role in account_admin.roles]
        return [self._get_aggregate(role) for role in role_ids]

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(PermissionsEnumTranscoding())
        transcoder.register(GenderEnumTranscoding())
        transcoder.register(AccountStatusEnumTranscoding())
        transcoder.register(RoleAggregateTranscoding())
        # transcoder.register(BytesTranscoding())
        transcoder.register(TransactionMethodEnumTranscoding())

    def create_role(self, name: str, permissions: List[PermissionsEnum]) -> UUID:
        role = RoleAggregate.create(
            name=name,
            permissions=permissions
        )
        self.save_aggregate_to_query_table(aggregate=role, **asdict(role))
        self.save(role)
        return role.id

    def append_permisson_to_role(self, role_id: UUID, permission: PermissionsEnum):
        role: RoleAggregate = self.repository.get(aggregate_id=role_id)
        role.append_permission(permission=permission)
        self.save_aggregate_to_query_table(aggregate=role)
        self.save(role)

    def create_account(
            self,
            owner_id: UUID,
            adimin_id: UUID,
            beggining_balance: float = 0,
            overdraft_protection: bool = False
    ) -> UUID:

        account = BankAccount.create(
            balance=beggining_balance,
            owner_id=owner_id,
            admin_id=adimin_id,
            overdraft_protection=overdraft_protection
        )

        account_owner: ChildAggregate = self.repository.get(aggregate_id=owner_id)
        account_admin: AdultAggregate = self.repository.get(aggregate_id=adimin_id)

        account_owner.set_related_account_id(account.id)
        account_admin.set_related_account_id(account.id)

        self.save_aggregate_to_query_table(account_owner, table_id='child_table')
        self.save_aggregate_to_query_table(account_admin, table_id='adult_table')
        self.save_aggregate_to_query_table(account, table_id='account_table')

        self.save(account, account_owner, account_admin)
        return account.id

    def create_parent(self, first_name: str, last_name: str, email: str) -> UUID:

        adult_account = AdultAggregate.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            roles=[]
        )

        self.save_aggregate_to_query_table(
            _id=adult_account.id,
            aggregate=adult_account,
            table_id='adult_table',
            **asdict(adult_account)
        )

        self.save(adult_account)
        return adult_account.id

    def create_child(self, first_name: str, last_name: str, email: str, gender: GenderEnum, age: int, grade: int):
        child = ChildAggregate.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            gender=gender,
            age=age,
            grade=grade
        )

        self.save_aggregate_to_query_table(
            aggregate=child,
            _id=child.id,
            table_id='child_table',
            **asdict(child)
        )

        self.save(child)
        return child.id

    def get_children():
        return query_table_dao.scan_child_aggregates()

    def create_task(self, name, description, due_date, value, assignee) -> UUID:
        task = TaskAggregate(
            name=name,
            description=description,
            due_date=due_date,
            value=value,
            attachments=[],
            items=[],
            assignee=assignee
        )
        self.save_aggregate_to_query_table(aggregate=task, table_id='task_table')
        self.save(task)
        return task.id

    def validate_task(self, task_id: UUID):
        task: TaskAggregate = self.repository.get(task_id)
        task.set_validated()
        self.save_aggregate_to_query_table(task, table_id='task_table')
        self.save(task)

    def mark_task_complete(self, task_id: UUID):
        task: TaskAggregate = self.repository.get(task_id)
        task_assignee: ChildAggregate = self.repository.get(task.assignee)
        account: BankAccount = self.repository.get(task_assignee.related_account_id)
        if task.is_complete:
            raise AssertionError("Task already complete!")

        task.set_complete()
        if task.is_validated:
            account.change_balance(method=TransactionMethodEnum.ADD, value=task.value)
        else:
            raise AssertionError("Task Has not been validate")

        self.save_aggregate_to_query_table(task, table_id='task_table')
        self.save_aggregate_to_query_table(account, table_id='account_table')
        self.save(account, task)

    def create_and_assign_task(self, child_id: UUID, name, description, due_date, value):
        child_aggregate: ChildAggregate = self.repository.get(child_id)
        task_id = self.create_task(
            name=name,
            assignee=child_aggregate.id,
            description=description,
            due_date=due_date,
            value=value
        )

        child_aggregate.add_task_id(task_id)

        self.save(child_aggregate)
        self.save_aggregate_to_query_table(aggregate=child_aggregate, table_id='child_table')
        return task_id

    def append_role_to_account(self, account_id: UUID, role_id: UUID):
        _account: UserAccountAggregate = self.repository.get(account_id)
        _account.add_role(role_id=role_id)
        self.save_aggregate_to_query_table(aggregate=_account)
        self.save(_account)

    def scan_aggregates(self):
        ids = self._list_originator_ids()
        return [
            self.repository.get(aggregate_id=_id) for _id in ids
        ]

    def change_account_balance(self, account_id: UUID, val: float, transaction_method: str):
        transaction_method = TransactionMethodEnum(transaction_method)

        account: BankAccount = self.repository.get(aggregate_id=account_id)

        account.change_balance(method=transaction_method, value=val)
        self.save_aggregate_to_query_table(account, table_id='account_table')
        self.save(account)
        return account.id

    def change_account_status(self, account_id: UUID, status: int) -> UUID:
        status = AccountStatusEnum(status)
        account = self.get_account(account_id=account_id)
        account_admin = self.get_account_admin(admin_id=account.admin_id)

        roles = self.get_role_aggeragates(role_ids=account_admin.roles)

        if verify_role_permissions(
                roles=roles,
                expected_permissions=[
                    PermissionsEnum.ADMIN,
                    PermissionsEnum.AccountChangeStatus
                ]
        ):
            account.change_status(status=AccountStatusEnum.INACTIVE)
            self.save(account)
            return account.id

    def get_account(self, account_id: UUID, version=None) -> BankAccount:
        return self._get_aggregate(account_id, version=version)

    def get_account_admin(self, admin_id: UUID) -> AdultAggregate:
        return self._get_aggregate(admin_id)

    def get_accounts(self, account_ids: List[UUID]) -> List[BankAccount]:
        _accounts = [self._get_aggregate(account_id) for account_id in account_ids]
        if self._validate_items_type(items=_accounts, expected_type=BankAccount):
            return _accounts

    def get_role_aggeragates(self, role_ids: List[UUID]) -> List[RoleAggregate]:
        roles = [self._get_aggregate(_id) for _id in role_ids]
        if self._validate_items_type(items=roles, expected_type=RoleAggregate):
            return roles

from typing import List, Dict
from uuid import UUID

from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder, InfrastructureFactory
from src.const import IN_PRODUCTION
from src.data_access.query_table_dao import QueryTableDAO
from src.domains.bank_domain import (
    BankAccount,
    ChildAggregate,
    RoleAggregate,
    AdultAggregate
)
from src.domains.task_domain import (
    TaskAggregate
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
from src.policy.bank_policies import (
    AccountOverdraftCheckPolicy
)
from src.transcoders import (
    PermissionsEnumTranscoding,
    AccountStatusEnumTranscoding,
    GenderEnumTranscoding,
    RoleAggregateTranscoding,
    TransactionMethodEnumTranscoding
)
from src.utils.aggregate_utils import verify_role_permissions

query_table_dao = QueryTableDAO(db_host="192.168.1.5", db_port=27017, db_name="BOE")


class BOEApplication(Application):

    # def __init__(self):
    #     super().__init__()

    # self.events.recorder = MongoRecorder(db_host='192.168.1.5', db_port=27017)

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

    def _get_aggregate(self, aggregate_id: UUID):
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
        role = RoleAggregate(
            name=name,
            permissions=permissions
        )

        self.save(role)
        return role.id

    def create_new_account(
            self,
            owner_first_name: str,
            owner_last_name: str,
            owner_email: str,
            owner_age: int,
            owner_grade: int,
            admin_first_name: str,
            admin_last_name: str,
            admin_email: str,
            owner_gender: GenderEnum,
            beggining_balance: float = 0,
            overdraft_protection: bool = False
    ) -> Dict[str, UUID]:
        admin_role = RoleAggregate(
            name="AdminRole",
            permissions=[PermissionsEnum.ADMIN]
        )

        owner_role = RoleAggregate(
            name='AccountOwnerRole',
            permissions=[PermissionsEnum.AccountOwner]
        )

        account_owner = ChildAggregate(
            first_name=owner_first_name,
            last_name=owner_last_name,
            email=owner_email,
            grade=owner_grade,
            age=owner_age,
            gender=owner_gender,
            roles=[owner_role.id]
        )

        admin = AdultAggregate(
            first_name=admin_first_name,
            last_name=admin_last_name,
            email=admin_email,
            roles=[admin_role.id]
        )

        account = BankAccount.create(
            balance=beggining_balance,
            owner_id=account_owner.id,
            admin_id=admin.id,
            overdraft_protection=overdraft_protection
        )
        print(account.id)
        print(BankAccount.create_id(owner_id=account_owner.id))
        self.save(admin_role, admin, owner_role, account, account_owner)
        return {
            "admin_role_id": admin_role.id,
            "admin_id": admin.id,
            "owner_role_id": owner_role.id,
            "account_id": account.id,
            "account_owner_id": account_owner.id,
        }

    def create_new_parent(self, first_name, last_name, email, role_name, permissions) -> Dict[str, UUID]:
        parent_role = RoleAggregate(
            name=role_name,
            permissions=permissions
        )
        adult_account = AdultAggregate(
            first_name=first_name,
            last_name=last_name,
            email=email,
            roles=[parent_role.id]

        )
        self.save(adult_account, parent_role)
        query_table_dao.add_account(
            _id=adult_account.id,
            first_name=adult_account.first_name,
            last_name=adult_account.last_name,
            email=adult_account.email
        )

        return {
            "parent_role_id": parent_role.id,
            "parent_account_id": adult_account.id
        }

    def create_task(self, name, description, due_date) -> UUID:
        task = TaskAggregate(
            name=name,
            description=description,
            due_date=due_date,
            attachments=[],
            items=[],
            assignee=''
        )
        self.save(task)
        return task.id

    def scan_aggregates(self):
        ids = self._list_originator_ids()
        return [
            self.repository.get(aggregate_id=_id) for _id in ids
        ]

    def change_account_balance(self, account_id: UUID, val: float, transaction_method: str):
        transaction_method = TransactionMethodEnum(transaction_method)

        account = self.repository.get(aggregate_id=account_id)
        account: BankAccount
        account_admin = self.repository.get(aggregate_id=account.admin_id)
        account_admin: AdultAggregate

        #
        role_aggreates = [self.repository.get(_id) for _id in account_admin.roles]
        #
        if AccountOverdraftCheckPolicy(bank_accout=account, new_amount=val, roles=role_aggreates).evaluate():
            account.change_balance(method=transaction_method, value=val)
            self.save(account)

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

    def get_account(self, account_id: UUID) -> BankAccount:
        return self._get_aggregate(account_id)

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

from uuid import UUID

from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder
from src.domains.bank_domain import (
    BankAccount,
    ChildAggregate,
    RoleAggregate,
    AdultAggregate
)
from src.domains.user_domain import (
    UserAccountAggregate
)
from src.domains.task_domain import (
    TaskAggregate
)
from src.enums import (
    GenderEnum,
    PermissionsEnum,
    AccountStatusEnum
)
from src.transcoders import (
    PermissionsEnumTranscoding,
    AccountStatusEnumTranscoding,
    GenderEnumTranscoding,
    RoleAggregateTranscoding
)
from src.utils.aggregate_utils import MongoRecorder

class BOEApplication(Application):

    def __init__(self):
        super(BOEApplication, self).__init__()
        self.events.recorder = MongoRecorder(db_host='192.168.1.5', db_port=27017)

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

    def create_new_accout(
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
            beggining_balance: float = 0
    ) -> BankAccount:
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

        account = BankAccount(
            balance=beggining_balance,
            owner=account_owner.id,
            admin=admin.id
        )
        self.save(admin_role, admin, owner_role, account, account_owner)
        return account

    def get_account(self, aggregate_id: UUID):
        return self._get_aggregate(aggregate_id)

    def create_new_parent(self, first_name, last_name, email, role_name, permissions):
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

        return adult_account

    def set_account_inactive(self, aggregate_id: UUID):
        account = self.repository.get(aggregate_id=aggregate_id)
        account: BankAccount

        account_admin = self._get_aggregate(aggregate_id=account.admin)

        account.change_status(
            status=AccountStatusEnum.INACTIVE,
            roles=self._get_roles_from_account_aggregate(account_admin=account_admin)
        )

        self.save(account)

    def create_task(self, name, description, due_date) -> TaskAggregate:
        task = TaskAggregate(
            name=name,
            description=description,
            due_date=due_date,
            attachments=[],
            items=[],
            assignee=''
        )
        self.save(task)
        return task


from uuid import UUID

from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder
from src.domains.bank_domain import BankAccount, ChildAggregate, RoleAggregate, AdultAggregate
from src.domains.user_domain import GenderEnum, PermissionsEnum
from src.enums import AccountStatusEnum
from src.transcoders import PermissionsEnumTranscoding, AccountStatusEnumTranscoding, GenderEnumTranscoding, \
    RoleAggregateTranscoding


class BOEApplication(Application):
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
        return self.repository.get(aggregate_id)

    def set_account_inactive(self, aggregate_id: UUID):
        account = self.repository.get(aggregate_id=aggregate_id)
        account: BankAccount

        account_admin = self.repository.get(aggregate_id=account.admin)
        role_ids = [role for role in account_admin.roles]
        roles = [self.repository.get(role) for role in role_ids]

        account.change_status(status=AccountStatusEnum.INACTIVE, roles=roles)

        self.save(account)

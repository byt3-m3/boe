from typing import List
from uuid import UUID

from cbaxter1988_utils import log_utils
from eventsourcing.application import Application
from eventsourcing.persistence import Transcoder
from src.domains.bank_domain.services.bank_services import (
    AccountManagementService,
)
from src.domains.task_domain.entities.task import Task
from src.domains.task_domain.services.task_services import TaskManagementService
from src.domains.task_domain.value_objects.task import TaskItem
from src.domains.users_domain.services.user_services import (
    UserManagementService
)
from src.enums import (
    GenderEnum,
    TaskState
)
from src.transcoders import (
    GenderEnumTranscoding,
    BankAccountStateTranscoding
)

logger = log_utils.get_logger(__name__)


class IdentityManagerApplication(Application):

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(GenderEnumTranscoding())

    def __init__(self):
        super().__init__()
        self.user_manager_service = UserManagementService()

    def create_role(self, role_name, permissions) -> UUID:
        role = self.user_manager_service.create_role(
            role_name=role_name,
            permissions=permissions
        )
        self.save(role)

        return role.id

    def create_child_account(
            self,
            first_name: str,
            last_name: str,
            age: int,
            roles: List[UUID],
            gender: GenderEnum
    ) -> UUID:
        child = self.user_manager_service.create_child_account(
            first_name=first_name,
            last_name=last_name,
            age=age,
            roles=roles,
            gender=gender
        )
        self.save(child)
        return child.id

    def create_user_account(
            self,
            first_name: str,
            last_name: str,
            roles: List[UUID],
    ):
        account = self.user_manager_service.create_user_account(
            first_name=first_name,
            last_name=last_name,
            roles=roles
        )
        self.save(account)
        return account.id


class BankManagerApplication(Application):

    def register_transcodings(self, transcoder: Transcoder):
        super().register_transcodings(transcoder)
        transcoder.register(BankAccountStateTranscoding())

    def __init__(self, identity_app: IdentityManagerApplication = None):
        super().__init__()
        self.bank_management_service = AccountManagementService()
        self.identity_manager_app = identity_app if identity_app else IdentityManagerApplication()

    def establish_new_account(
            self,
            first_name: str,
            last_name: str,
            age: int,
            gender: GenderEnum,
            overdraft_protection: bool = True,
            roles: List[UUID] = None,
    ):
        _child_id = self.identity_manager_app.create_child_account(
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            roles=roles
        )

        _bank_account = self.bank_management_service.create_account(
            owner_id=_child_id,
            overdraft_protection=overdraft_protection
        )

        self.save(_bank_account)
        return _bank_account.id


class TaskManagerApplication(Application):
    def __init__(self):
        super().__init__()
        self.task_management_service = TaskManagementService()

    def create_task(
            self,
            description: str,
            name: str,
            value: int,
            due_date: int,
            assignee_id: UUID = None,
            state: TaskState = TaskState.ENABLED,
            items: List[TaskItem] = None,
    ) -> UUID:
        if items is None:
            items = []

        if assignee_id:
            state = TaskState.ASSIGNED

        task = self.task_management_service.create_task(
            assignee_id=assignee_id,
            description=description,
            name=name,
            state=state,
            due_date=due_date,
            items=items,
            value=value
        )
        logger.debug(f"Created: {task.id}")
        self.save(task)

        return task.id

    def append_item_to_task(self, task_id: UUID, task_item: TaskItem) -> UUID:
        task: Task = self.repository.get(aggregate_id=task_id)
        logger.info(f"Appending {task_item} to {task_id}")
        task.add_item(task_item=task_item)
        self.save(task)
        return task.id


class BOESystem:

    def __init__(self):
        self.identity_app = IdentityManagerApplication()
        self.bank_app = BankManagerApplication(identity_app=self.identity_app)
        self.task_app = TaskManagerApplication()

    def establish_new_account(
            self,
            first_name: str,
            last_name: str,
            age: int,
            gender: GenderEnum,
            overdraft_protection: bool = True,
            roles: List[UUID] = None,
    ):
        return self.bank_app.establish_new_account(
            first_name=first_name,
            last_name=last_name,
            age=age,
            gender=gender,
            overdraft_protection=overdraft_protection,
            roles=roles
        )

    def create_role(self, role_name, permissions) -> UUID:
        return self.identity_app.create_role(
            role_name=role_name,
            permissions=permissions
        )

    def create_child_account(
            self,
            first_name: str,
            last_name: str,
            age: int,
            roles: List[UUID],
            gender: GenderEnum
    ) -> UUID:
        return self.identity_app.create_child_account(
            first_name=first_name,
            last_name=last_name,
            age=age,
            roles=roles,
            gender=gender
        )

    def create_task(
            self,
            description: str,
            name: str,
            value: int,
            due_date: int,
            assignee_id: UUID = None,
            state: TaskState = TaskState.ENABLED,
            items: List[TaskItem] = None,
    ) -> UUID:
        return self.task_app.create_task(
            description=description,
            name=name,
            value=value,
            due_date=due_date,
            assignee_id=assignee_id,
            state=state,
            items=items
        )

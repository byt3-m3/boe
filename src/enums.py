from enum import Enum


class PermissionsEnum(Enum):
    ADMIN = 0
    AccountChangeBalance = 1
    AccountChangeStatus = 2
    AccountAdminModifyPermissions = 3
    AccountSetOverdraft = 4
    AccountModifyOverdraftProtection = 5
    AccountClearOverDraft = 6
    AccountAddAccountAdmin = 7
    AccountDeleteAccountAdmin = 8
    Parent = 98
    AccountOwner = 99
    Child = 100


class GenderEnum(Enum):
    MALE = 1
    FEMALE = 2

class AccountStatusEnum(Enum):
    ACTIVE = 1
    INACTIVE = 2
    OVER_DRAFTED = 3

class BankAccountStateEnum(Enum):
    OPEN = 1
    OVER_DRAFTED = 2
    CLOSED = 99

class TransactionMethodEnum(Enum):
    ADD = 1
    SUBTRACT = 2


class TaskState(Enum):
    ENABLED = 1
    ASSIGNED = 2
    OVER_DUE = 3
    WORK_COMPLETED = 4
    PENDING_VALIDATION = 5
    AWARDED = 7
    DISABLED = 99
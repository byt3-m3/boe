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


class GenderEnum(Enum):
    MALE = 1
    FEMALE = 2

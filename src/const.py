from src.enums import PermissionsEnum

PERMISSION_MAP = {
    "bank_domain_change_account_balance": [
        PermissionsEnum.ADMIN,
        PermissionsEnum.AccountChangeBalance,
    ]
}

IN_PRODUCTION = False
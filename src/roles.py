from src.enums import PermissionsEnum

class _SystemRole:
    name = "AdminRole"
    permissions = [
        PermissionsEnum.ADMIN,
        PermissionsEnum.AccountSetOverdraft
    ]

system_role = _SystemRole()
from src.domains.user_domain import RoleAggregate
from src.enums import PermissionsEnum

system_role = RoleAggregate(
    name="AdminRole",
    permissions=[
        PermissionsEnum.ADMIN,
        PermissionsEnum.AccountSetOverdraft
    ]
)

SystemParentRole = RoleAggregate(
    name="SystemParentRole",
    permissions=[
        PermissionsEnum.Parent
    ]
)

SystemChildRole = RoleAggregate(
    name="SystemChildRole",
    permissions=[
        PermissionsEnum.Child
    ]
)

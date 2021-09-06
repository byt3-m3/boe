from src.models.user_models import RoleModel
from src.enums import PermissionsEnum

class AdminRole(RoleModel):
    name = "AdminRole"
    permissions = [
        PermissionsEnum.ADMIN
    ]
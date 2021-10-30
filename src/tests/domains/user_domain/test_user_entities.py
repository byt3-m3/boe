from src.enums import PermissionsEnum


def test_user_account_append_role(user_account, child_role):
    user_account.append_role(role_id=child_role.id)
    assert len(user_account.roles) == 2


def test_user_account_remove_role(user_account, child_role):
    user_account.append_role(role_id=child_role.id)
    user_account.remove_role(role_id=child_role.id)
    assert len(user_account.roles) == 1


def test_role_append_permission(child_role):
    child_role.append_permission(PermissionsEnum.AccountSetOverdraft)
    assert len(child_role.permissions) == 2

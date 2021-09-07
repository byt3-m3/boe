from pytest import fixture
from src.domains.user_domain import RoleAggregate
from src.enums import PermissionsEnum
from src.models.user_models import RoleDataModel


@fixture
def role_data_model():
    yield RoleDataModel(
        name="test_role"

    )


@fixture
def role_aggregate(role_data_model):
    yield RoleAggregate(
        model=role_data_model,
        permissions=[PermissionsEnum.ADMIN]
    )

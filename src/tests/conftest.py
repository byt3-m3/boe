from pytest import fixture
from src.domains.user_domain import RoleAggregate
from src.enums import PermissionsEnum, GenderEnum
from src.models.user_models import RoleDataModel, ChildDataModel, AdultDataModel


@fixture
def adult_data_model():
    return AdultDataModel(
        first_name="test_name",
        last_name="test_name",
        email="test@gmail.com",

    )


@fixture
def child_data_model():
    return ChildDataModel(
        first_name="test_name",
        last_name="test_name",
        email="test@gmail.com",
        age=5,
        grade=3,
        gender=GenderEnum.MALE

    )


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

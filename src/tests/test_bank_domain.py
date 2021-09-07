from pytest import fixture
from src.domains.bank_domain import (
    BankAccount,
    AccountAdmin
)
from src.enums import (
    PermissionsEnum,
    TransactionMethodEnum,
    AccountStatusEnum
)
from src.models.bank_models import (
    BankAccountDataModel,
    AccountOwnerDataModel,
    AccountAdminDataModel

)


@fixture
def account_admin_data_model():
    return AccountAdminDataModel(

    )


@fixture
def account_owner_data_model():
    return AccountOwnerDataModel(

    )


@fixture
def bank_account_data_model(account_owner_data_model):
    return BankAccountDataModel(
        balance=0,
        owner=account_owner_data_model,
    )


@fixture
def account_admin_aggregate(role_aggregate):
    return AccountAdmin(
        role=role_aggregate
    )


@fixture
def bank_account_aggregate(bank_account_data_model, account_admin_aggregate):
    return BankAccount(
        model=bank_account_data_model,
    )


@fixture
def bank_account_w_protection_aggregate(bank_account_data_model, account_admin_aggregate):
    return BankAccount(
        model=bank_account_data_model,
        overdraft_protection=True
    )


def test_bank_account_verify_role_permissions(bank_account_aggregate, role_aggregate):
    bank_account_aggregate._verify_role_permissions(role=role_aggregate, expected_permissions=[PermissionsEnum.ADMIN])


def test_bank_account_change_balance_add(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.change_balance(
        method=TransactionMethodEnum.ADD,
        value=10,
        role=role_aggregate
    )

    assert subject.model.balance == 10


def test_bank_account_change_balance_subtract(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.change_balance(
        method=TransactionMethodEnum.SUBTRACT,
        value=10,
        role=role_aggregate
    )

    assert subject.model.balance == -10


def test_bank_account_w_protection_change_balance_subtract(bank_account_w_protection_aggregate, role_aggregate):
    subject = bank_account_w_protection_aggregate
    subject.change_balance(
        method=TransactionMethodEnum.SUBTRACT,
        value=10,
        role=role_aggregate
    )
    events = subject.collect_events()

    assert isinstance(events[1], subject.OverDraftProtectionEvent)
    assert subject.model.balance == 0


def test_bank_account_change_status(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.change_status(status=AccountStatusEnum.INACTIVE, role=role_aggregate)

    assert subject.status == AccountStatusEnum.INACTIVE


def test_bank_account_enable_overdraft_protection(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.enable_overdraft_protection(role=role_aggregate)
    events = subject.collect_events()

    assert isinstance(events[1], subject.EnableOverDraftProtection)
    assert subject.overdraft_protection == True


def test_bank_account_disable_overdraft_protection(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.disable_overdraft_protection(role=role_aggregate)
    events = subject.collect_events()

    assert isinstance(events[1], subject.DisableOverDraftProtection)
    assert subject.overdraft_protection == False


def test_bank_account_trigger_overdraft(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    assert subject.is_overdrafted == False
    subject.trigger_overdraft(status=True, role=role_aggregate)
    events = subject.collect_events()

    assert isinstance(events[1], subject.TriggerOverDraft)
    assert subject.is_overdrafted == True

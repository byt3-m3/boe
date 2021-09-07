from pytest import fixture
from src.domains.bank_domain import (
    BankAccount,
    AccountAdmin,
    AccountOwner
)
from src.enums import (
    PermissionsEnum,
    TransactionMethodEnum,
    AccountStatusEnum
)
from src.models.bank_models import (
    BankAccountDataModel,

)
from src.utils.core_utils import clone_item


@fixture
def account_admin_data_model():
    return AccountAdminDataModel(

    )


@fixture
def bank_account_data_model():
    return BankAccountDataModel(
        balance=0,

    )


@fixture
def account_admin_aggregate(role_aggregate, adult_data_model):
    return AccountAdmin(
        role=role_aggregate,
        model=adult_data_model
    )


@fixture
def bank_account_aggregate(bank_account_data_model, bank_account_owner_aggregate):
    return BankAccount(
        model=bank_account_data_model,
        owner=bank_account_owner_aggregate
    )


@fixture
def bank_account_w_protection_aggregate(bank_account_data_model, account_admin_aggregate, bank_account_owner_aggregate):
    model = clone_item(bank_account_data_model)
    model.overdraft_protection = True
    return BankAccount(
        model=model,
        owner=bank_account_owner_aggregate
    )


@fixture
def bank_account_owner_aggregate(child_data_model):
    return AccountOwner(
        model=child_data_model
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
    events = subject.collect_events()

    assert isinstance(events[1], subject.TriggerOverDraft)
    assert subject.model.balance == -10
    assert subject.model.is_overdrafted is True


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
    assert subject.model.is_overdrafted is False


def test_bank_account_change_status(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.change_status(status=AccountStatusEnum.INACTIVE, role=role_aggregate)

    assert subject.model.status == AccountStatusEnum.INACTIVE


def test_bank_account_enable_overdraft_protection(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.enable_overdraft_protection(role=role_aggregate)
    events = subject.collect_events()

    assert isinstance(events[1], subject.EnableOverDraftProtection)
    assert subject.model.overdraft_protection == True


def test_bank_account_disable_overdraft_protection(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.disable_overdraft_protection(role=role_aggregate)
    events = subject.collect_events()

    assert isinstance(events[1], subject.DisableOverDraftProtection)
    assert subject.model.overdraft_protection == False


def test_bank_account_trigger_overdraft(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    assert subject.model.is_overdrafted == False
    subject.trigger_overdraft(status=True, role=role_aggregate)
    events = subject.collect_events()

    assert isinstance(events[1], subject.TriggerOverDraft)
    assert subject.model.is_overdrafted == True

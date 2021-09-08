from pytest import fixture
from src.domains.bank_domain import (
    BankAccount
)
from src.enums import (
    PermissionsEnum,
    TransactionMethodEnum,
    AccountStatusEnum
)


@fixture
def bank_account_aggregate():
    return BankAccount(
        balance=0,
    )


@fixture
def bank_account_w_protection_aggregate():
    return BankAccount(
        overdraft_protection=True,
        balance=0
    )


def test_bank_account_verify_role_permissions(bank_account_aggregate, role_aggregate):
    bank_account_aggregate._verify_role_permissions(roles=[role_aggregate],
                                                    expected_permissions=[PermissionsEnum.ADMIN])


def test_bank_account_change_balance_add(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.change_balance(
        method=TransactionMethodEnum.ADD,
        value=10,
        roles=[role_aggregate]
    )

    assert subject.balance == 10


def test_bank_account_change_balance_subtract(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.change_balance(
        method=TransactionMethodEnum.SUBTRACT,
        value=10,
        roles=[role_aggregate]
    )
    events = subject.collect_events()

    assert isinstance(events[1], subject.TriggerOverDraft)
    assert subject.balance == -10
    assert subject.is_overdrafted is True


def test_bank_account_w_protection_change_balance_subtract(bank_account_w_protection_aggregate, role_aggregate):
    subject = bank_account_w_protection_aggregate
    subject.change_balance(
        method=TransactionMethodEnum.SUBTRACT,
        value=10,
        roles=[role_aggregate]
    )
    events = subject.collect_events()

    assert isinstance(events[1], subject.OverDraftProtectionEvent)
    assert subject.balance == 0
    assert subject.is_overdrafted is False


def test_bank_account_change_status(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.change_status(status=AccountStatusEnum.INACTIVE, roles=[role_aggregate])

    assert subject.status == AccountStatusEnum.INACTIVE


def test_bank_account_enable_overdraft_protection(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.enable_overdraft_protection(roles=[role_aggregate])
    events = subject.collect_events()

    assert isinstance(events[1], subject.EnableOverDraftProtection)
    assert subject.overdraft_protection == True


def test_bank_account_disable_overdraft_protection(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    subject.disable_overdraft_protection(roles=[role_aggregate])
    events = subject.collect_events()

    assert isinstance(events[1], subject.DisableOverDraftProtection)
    assert subject.overdraft_protection == False


def test_bank_account_trigger_overdraft(bank_account_aggregate, role_aggregate):
    subject = bank_account_aggregate
    assert subject.is_overdrafted == False
    subject.trigger_overdraft(status=True, roles=[role_aggregate])
    events = subject.collect_events()

    assert isinstance(events[1], subject.TriggerOverDraft)
    assert subject.is_overdrafted == True


def test_bank_account_update_owner(bank_account_aggregate, child_aggregate):
    bank_account_aggregate.update_owner(child_aggregate=child_aggregate)
    assert bank_account_aggregate.owner == child_aggregate.id


def test_bank_account_update_admin(bank_account_aggregate, adult_aggregate):
    bank_account_aggregate.update_admin(adult_aggregate=adult_aggregate)
    assert bank_account_aggregate.admin == adult_aggregate.id

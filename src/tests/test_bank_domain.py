import pytest
from pytest import fixture
from src.domains.bank_domain import BankAccount, AccountAdmin, AccountOwner, TransactionMethodEnum
from src.enums import PermissionsEnum
from src.models.user_models import ParentModel
from src.roles import AdminRole
@fixture()
def account_admin_aggregate():
    yield AccountAdmin(
        user_model=ParentModel(
            first_name="test_name",
            last_name="test_name",
            email="test@gmail.com",
            roles=AdminRole()
        ),
        permissions=[PermissionsEnum.ADMIN]
    )


@fixture()
def account_owner_aggregate():
    yield AccountOwner(
        name='test_owner'
    )


@fixture()
def bank_account_aggregate(account_admin_aggregate, account_owner_aggregate):
    yield BankAccount(
        owner=account_owner_aggregate,
        overdraft_protection=True,
        balance=0,
        admin_map={account_admin_aggregate.id: account_admin_aggregate}
    )


def test_bank_account_change_balance_add(bank_account_aggregate, account_admin_aggregate):
    testable = bank_account_aggregate
    testable: BankAccount

    testable.change_balance(
        method=TransactionMethodEnum.ADD,
        value=10,
        admin=account_admin_aggregate
    )

    events = testable.collect_events()

    assert testable.balance == 10
    assert isinstance(events[len(events) - 1], testable.ChangeAccountBalanceEvent)
    assert testable.overdrafted is False


def test_bank_account_change_balance_subtract_w_overdraft_protection(bank_account_aggregate, account_admin_aggregate):
    testable = bank_account_aggregate
    testable: BankAccount

    testable.change_balance(
        method=TransactionMethodEnum.SUBTRACT,
        value=10,
        admin=account_admin_aggregate
    )

    events = testable.collect_events()
    assert testable.overdraft_protection is True
    assert testable.overdrafted is False
    assert testable.balance == 0
    assert isinstance(events[len(events) - 1], testable.ChangeAccountBalanceEvent)


def test_bank_account_change_balance_subtract_wo_overdraft_protection(bank_account_aggregate, account_admin_aggregate):
    testable = bank_account_aggregate
    testable: BankAccount

    testable.disable_overdraft_protection(admin=account_admin_aggregate)

    testable.change_balance(
        method=TransactionMethodEnum.SUBTRACT,
        value=10,
        admin=account_admin_aggregate
    )

    events = testable.collect_events()

    assert testable.overdrafted is True
    assert testable.balance == -10
    assert isinstance(events[len(events) - 1], testable.ChangeAccountBalanceEvent)
    assert isinstance(events[2], testable.AccountOverdraftedEvent)


def test_bank_account_invalid_permission(bank_account_aggregate, account_admin_aggregate):
    testable = bank_account_aggregate
    testable: BankAccount

    testable.delete_account_admin(account_admin_aggregate, target_id=account_admin_aggregate.id)
    with pytest.raises(PermissionError):
        testable.change_balance(
            method=TransactionMethodEnum.SUBTRACT,
            value=10,
            admin=account_admin_aggregate
        )

    events = testable.collect_events()

    assert testable.overdrafted is False
    assert testable.balance == 0
    assert isinstance(events[len(events) - 1], testable.PermissionEvent)

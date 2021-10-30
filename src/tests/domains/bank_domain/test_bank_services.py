from src.domains.bank_domain.services.bank_services import (
    AccountManagementService
)


def test_account_management_service_process_transaction_subtract(bank_account, subtract_transaction):
    service = AccountManagementService()
    bank_account.overdraft_protection = False
    service.process_transaction(account=bank_account, transaction=subtract_transaction)

    assert bank_account.is_overdrafted is True
    assert bank_account.balance == -50


def test_account_management_service_process_transaction_subtract_1(bank_account, subtract_transaction):
    service = AccountManagementService()
    service.process_transaction(account=bank_account, transaction=subtract_transaction)

    assert bank_account.is_overdrafted is False
    assert bank_account.balance == 0


def test_account_management_service_process_transaction_add(bank_account, add_transaction):
    service = AccountManagementService()
    service.process_transaction(account=bank_account, transaction=add_transaction)

    assert bank_account.is_overdrafted is False
    assert bank_account.balance == 50

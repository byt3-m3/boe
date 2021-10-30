from src.applications.system_apps import BankManagerApplication, BOESystem
from src.domains.bank_domain.entities.bank_account import BankAccount
from src.enums import GenderEnum


def test_bma_establish_new_account():
    app = BankManagerApplication()

    account_id = app.establish_new_account(
        age=7,
        first_name="Liam",
        last_name="Baxter",
        gender=GenderEnum.MALE
    )

    account = app.repository.get(aggregate_id=account_id)

    assert isinstance(account, BankAccount)


def test_boe_system_establish_new_account():
    system = BOESystem()

    account_id = system.establish_new_account(
        age=7,
        first_name="Liam",
        last_name="Baxter",
        gender=GenderEnum.MALE
    )



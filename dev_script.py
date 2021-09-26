from src.applications.boe_app import BOEApplication, GenderEnum, BankAccount, TransactionMethodEnum, BankAccount

from eventsourcing.persistence import StoredEvent, Mapper
import json
from uuid import UUID
app = BOEApplication()
import os

# account_id = app.create_new_account(
#     owner_first_name="Liam",
#     owner_last_name="Baxter",
#     owner_email="liam@gmail.com",
#     owner_age=6,
#     owner_grade=7,
#     owner_gender=GenderEnum.MALE,
#     admin_email="cbaxtertech@gmail.com",
#     admin_first_name="Courtney",
#     admin_last_name="Baxter",
#     overdraft_protection=True
#
# )

# aggregates = app.scan_bank_account_aggreates()
# print(aggregates)

test_aggregate = UUID('8564c4b94f9b4e97b994c55e98625bf6')
# test_aggregate = account_id


app.change_account_balance(
    account_id=test_aggregate,
    val=450, transaction_method=TransactionMethodEnum.ADD.value
)
account = app.get_account(account_id=test_aggregate)
# account: BankAccount
#
#
# print(app.repository.get(test_aggregate))
print(account)
print(account.version)
# print(app.scan_aggregates())
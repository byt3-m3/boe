from src.applications.boe_app import BOEApplication, GenderEnum, BankAccount

from eventsourcing.persistence import StoredEvent, Mapper
import json

app = BOEApplication()

account_id = app.create_new_account(
    owner_first_name="Liam",
    owner_last_name="Baxter",
    owner_email="liam@gmail.com",
    owner_age=6,
    owner_grade=7,
    owner_gender=GenderEnum.MALE,
    admin_email="cbaxtertech@gmail.com",
    admin_first_name="Courtney",
    admin_last_name="Baxter",
    overdraft_protection=True

)

aggregates = app.scan_aggregates()
for aggregate in aggregates:
    if isinstance(aggregate, BankAccount):
        print(aggregate)

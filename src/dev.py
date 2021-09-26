import os
from datetime import datetime, timedelta

import requests
from src.applications.boe_app import BOEApplication, PermissionsEnum, query_table_dao, GenderEnum, TransactionMethodEnum

INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory";
SQLITE_DBNAME = "_db/prod_db"

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

headers = {
    "content_type": "application/json"
}


def main():
    app = BOEApplication()
    #
    role_id, child_id = app.setup()
    parent_id = app.create_parent(
        first_name='minh',
        last_name='baxter',
        email='minh.baxter@gmail.com',

    )
    #
    child_id = app.create_child(
        first_name='john',
        last_name='baxter',
        email='joe.baxter@gmail.com',
        gender=GenderEnum.MALE,
        age=8,
        grade=3
    )

    #

    # items = query_table_dao.query_child(query={"email": "joe.baxter@gmail.com"})
    # items = query_table_dao.query_role(query={"name": "AdminRole"})
    items = query_table_dao.scan_adult_aggregates()

    app.append_permisson_to_role(role_id=role_id, permission=PermissionsEnum.AccountChangeBalance)
    app.append_role_to_account(account_id=parent_id, role_id=role_id)
    print(items)
    #
    # print(account_id)
    # app.create_task(
    #     name="Clean Your Room",
    #     description="I want your room clean",
    #     value=200,
    #     due_date=datetime.datetime.now()
    # )

    account_id = app.create_account(
        owner_id=child_id,
        adimin_id=parent_id,
        overdraft_protection=True

    )
    app.change_account_balance(account_id=account_id, val=70, transaction_method=TransactionMethodEnum.ADD)
    app.change_account_balance(account_id=account_id, val=50, transaction_method=TransactionMethodEnum.ADD)
    app.change_account_balance(account_id=account_id, val=20, transaction_method=TransactionMethodEnum.SUBTRACT)


def api_create_child():
    payload = {
        "first_name": "liam",
        "last_name": "Baxter",
        "email": "liam@gmail.com",
        "gender": 1,
        "age": 5,
        "grade": 8,
    }
    response = requests.post(
        url="http://127.0.0.1:5000/api/v1/users/child",
        json=payload,
    )
    print(response.json())
    if response.status_code in [200, 417]:
        response_data = response.json()
        return response_data['id']


def api_get_child():
    child_id = '1b417d26-e413-5407-8f7f-b632c4afb1e4'
    response = requests.get(f"http://127.0.0.1:5000/api/v1/users/child/{child_id}")
    print(response.json())


def api_get_get_account():
    account_id = "fd3c2347680955f28788f54323336eff"
    response = requests.get(f"http://127.0.0.1:5000/api/v1/account/{account_id}")
    print(response)


def api_create_account():
    admin_id = "1b417d26-e413-5407-8f7f-b632c4afb1e4"
    child_id = "d95effc8-ca27-591a-8655-33603fe3c022"

    payload = {
        "admin_id": admin_id,
        "owner_id": child_id,
        "overdraft_protection": True

    }

    response = requests.post(
        url="http://127.0.0.1:5000/api/v1/account",
        json=payload,
        headers=headers
    )
    print(response.json())
    if response.status_code in [200, 417]:
        response_data = response.json()
        if response_data.get("id"):
            return response_data['id']


def api_create_adult():
    payload = {
        "first_name": "Courtney",
        "last_name": "Baxter",
        "email": "cbaxtertech@gmail.com"
    }
    response = requests.post(
        url="http://127.0.0.1:5000/api/v1/users/adult",
        json=payload,
    )

    if response.status_code in [200, 417]:
        response_data = response.json()
        return response_data['id']


def api_change_account_balace_add():
    account_id = "40a4f1cdf9e05af38d95f3b585c13f81"

    payload = {
        "account_id": account_id,
        "val": 50,
        "method": 1
    }

    response = requests.put(
        url="http://127.0.0.1:5000/api/v1/account/balance",
        json=payload,
        headers=headers
    )
    print(response.json())


def api_change_account_balace_subtract():
    account_id = "40a4f1cdf9e05af38d95f3b585c13f81"

    payload = {
        "account_id": account_id,
        "val": 50,
        "method": 2
    }

    response = requests.put(
        url="http://127.0.0.1:5000/api/v1/account/balance",
        json=payload,
        headers=headers
    )
    print(response.json())


def api_create_task():
    due_date_dt = datetime.now() + timedelta(days=5)
    payload = {
        "name": "Clean Your Room",
        "description": "Cleaning MY Room",
        "due_date": due_date_dt.timestamp(),
        "value": 50,
        "child_id": "d95effc8-ca27-591a-8655-33603fe3c022",
    }

    response = requests.post(
        url="http://127.0.0.1:5000/api/v1/task",
        json=payload,
    )
    print(response.json())
    return response.json()['id']

def api_validate_task(task_id):

    response = requests.get(
        url=f'http://127.0.0.1:5000/api/v1/task/{task_id}/validate'
    )
    print(response)

def api_complete_task(task_id):

    response = requests.get(
        url=f'http://127.0.0.1:5000/api/v1/task/{task_id}/done'
    )
    print(response)

if __name__ == "__main__":
    # child_id = api_create_child()
    # adult_id = api_create_adult()
    # account_id = api_create_account()
    # task_id = api_create_task()

    task_id = '7ba89f01-1359-4dce-84cf-8e0ed62f5339'
    api_validate_task(task_id=task_id)
    api_complete_task(task_id=task_id)

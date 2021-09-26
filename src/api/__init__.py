import json
import os
from uuid import UUID

from eventsourcing.persistence import IntegrityError
from flask import Flask, Response, request
from src.applications.boe_app import BOEApplication, GenderEnum
from src.enums import TransactionMethodEnum
from src.utils.core_utils import make_id

app = Flask(__name__)

headers = {
    "content_type": "application/json"
}

INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory";
SQLITE_DBNAME = "_db/prod_db"

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME

boe_app = BOEApplication()


@app.route("/api/v1/account", methods=["POST"])
def create_account():
    data = request.json

    owner_id = data.get("owner_id")
    admin_id = data.get("admin_id")
    overdraft_protection = data.get("overdraft_protection")

    try:
        account_id = boe_app.create_account(
            owner_id=UUID(owner_id),
            adimin_id=UUID(admin_id),
            overdraft_protection=overdraft_protection
        )

        return Response(response=json.dumps({"id": str(account_id)}))
    except IntegrityError:
        return Response(status=417, response=json.dumps(
            {"msg": f"Account Already Present with ID: "}))


@app.route("/api/v1/account/balance", methods=["PUT"])
def change_account_balance():
    data = request.json

    account_id = UUID(data.get("account_id"))
    val = data.get("val")
    method = TransactionMethodEnum(data.get("method"))

    try:
        account_id = boe_app.change_account_balance(
            account_id=account_id,
            val=val,
            transaction_method=method
        )
        account = boe_app.get_account(account_id=account_id)
        return Response(response=json.dumps({"new_balance": account.balance}), headers=headers)
    except IntegrityError:
        return Response(status=417, response=json.dumps(
            {"msg": f"Account Already Present with ID: "}))


@app.route("/api/v1/account/<account_id>", methods=["GET"])
def get_account(account_id):
    boe_app.get_account(account_id=UUID(account_id))
    data = request.json

    owner_id = data.get("owner_id")
    admin_id = data.get("admin_id")
    admin_id = data.get("overdraft_protection")

    boe_app.create_account()
    return Response


@app.route("/api/v1/users/child", methods=["POST"])
def create_child():
    request_boy = request.json
    try:
        child_id = boe_app.create_child(
            first_name=request_boy.get("first_name"),
            last_name=request_boy.get("last_name"),
            email=request_boy.get("email"),
            gender=GenderEnum(request_boy.get("gender")),
            age=request_boy.get("age"),
            grade=request_boy.get("grade")
        )
        return Response(status=200, response=json.dumps({"id": str(child_id)}), headers=headers)

    except IntegrityError:
        return Response(
            status=417,
            response=json.dumps(
                {
                    "msg": f"Account Already Present with ID: {make_id(domain='users', key=request_boy.get('email'))}",
                    "id": f"{make_id(domain='users', key=request_boy.get('email'))}"
                }
            )
        )


@app.route("/api/v1/users/adult", methods=["POST"])
def create_adult():
    request_body = request.json
    try:
        parent_id = boe_app.create_parent(
            first_name=request_body.get("first_name"),
            last_name=request_body.get("last_name"),
            email=request_body.get("email"),
        )
        return Response(status=200, response=json.dumps({"id": str(parent_id)}), headers=headers)

    except IntegrityError:
        return Response(
            status=417,
            response=json.dumps(
                {
                    "msg": f"Account Already Present with ID: {make_id(domain='users', key=request_boy.get('email'))}",
                    "id": f"{make_id(domain='users', key=request_boy.get('email'))}"
                }
            )
        )


@app.route("/api/v1/users/child/<child_id>", methods=["GET"])
def get_child(child_id):
    child = boe_app.repository.get(UUID(child_id))
    return Response(
        headers=headers,
        response=json.dumps(
            {
                "first_name": child.first_name,
                "last_name": child.last_name,
                "email": child.email,

            }
        )
    )


@app.route("/api/v1/task", methods=['POST'])
def create_task():
    request_body = request.json
    try:
        task_id = boe_app.create_and_assign_task(
            name=request_body.get("name"),
            description=request_body.get("description"),
            due_date=request_body.get("due_date"),
            value=request_body.get("value"),
            child_id=UUID(request_body.get("child_id"))
        )
        return Response(status=200, response=json.dumps({"id": str(task_id)}), headers=headers)

    except IntegrityError:
        return Response(
            status=417,
            response=json.dumps(
                {
                    "msg": f"Account Already Present with ID: {make_id(domain='users', key=request_boy.get('email'))}",
                    "id": f"{make_id(domain='users', key=request_boy.get('email'))}"
                }
            )
        )


@app.route("/api/v1/task/<task_id>/validate")
def validate_task(task_id):
    boe_app.validate_task(task_id=UUID(task_id))
    return Response(status=200, headers=headers, response={})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

import uuid

from flask import Flask, request

app = Flask(__name__)
from src.models.api_models.request_models import (
    CreateTaskRequest,
    CreatChildRequest,
    CreateAdultRequest
)
from dataclasses import asdict
from src.applications.boe_service import BOETaskService, BOEUserService
from cbaxter1988_utils import flask_utils
from src.enums import GenderEnum
from http import HTTPStatus
import os
from eventsourcing.persistence import IntegrityError
from src.utils.aggregate_utils import extract_type
INFRASTRUCTURE_FACTORY = "eventsourcing.sqlite:Factory"
SQLITE_DBNAME = "_db/prod_db"

os.environ['INFRASTRUCTURE_FACTORY'] = INFRASTRUCTURE_FACTORY
os.environ['SQLITE_DBNAME'] = SQLITE_DBNAME


@app.route("/api/v1/task", methods=["POST"])
def create_task():
    task_service = BOETaskService()

    data = request.json

    payload = CreateTaskRequest(**data.get("CreateTaskRequest"))

    task_uuid = task_service.create_task(**asdict(payload))
    return flask_utils.build_json_response(
        status=HTTPStatus.OK,
        payload={"id": str(task_uuid)}
    )


@app.route("/api/v1/account/child", methods=["POST"])
def create_account_child():
    user_service = BOEUserService()
    data = request.json

    create_child_request = data.get("CreateChildRequest")
    create_child_request['gender'] = GenderEnum(create_child_request['gender'])

    payload = CreatChildRequest(**create_child_request)

    try:
        child_id = user_service.create_child(**asdict(payload))
        return flask_utils.build_json_response(
            status=HTTPStatus.OK,
            payload={"id": str(child_id)}
        )
    except IntegrityError as err:
        return flask_utils.build_json_response(
            status=HTTPStatus.EXPECTATION_FAILED,
            payload={"exception": f"{err}", "msg": "Duplicate!"}
        )


@app.route("/api/v1/account/adult", methods=["POST"])
def create_account_adult():
    user_service = BOEUserService()
    data = request.json

    create_adult_request = data.get("CreateAdultRequest")

    payload = CreateAdultRequest(**create_adult_request)

    try:
        adult_id = user_service.create_adult(**asdict(payload))
        return flask_utils.build_json_response(
            status=HTTPStatus.OK,
            payload={"id": str(adult_id)}
        )

    except IntegrityError as err:
        return flask_utils.build_json_response(
            status=HTTPStatus.EXPECTATION_FAILED,
            payload={"exception": f"{err}", "msg": "Duplicate!"}
        )


@app.route("/api/v1/account/<account_id>", methods=["GET"])
def get_account(account_id):
    user_service = BOEUserService()
    account = user_service.repository.get(aggregate_id=uuid.UUID(account_id))
    type_str = extract_type(account)
    type_name = type_str[type_str.rfind(".")+1:]

    response = {
        type_name: account.serialize()
    }
    return flask_utils.build_json_response(
        status=HTTPStatus.OK,
        payload=response
    )


def main():
    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()

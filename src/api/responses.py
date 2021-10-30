from http import HTTPStatus

from cbaxter1988_utils.lib.flask_utils import build_json_response


def custom_response(status: HTTPStatus, payload: dict):
    return build_json_response(
        status=status,
        payload=payload
    )


def ok_response(msg=None):
    return build_json_response(
        status=HTTPStatus.ok,
        payload={"msg": msg}
    )


def created_response(msg=None):
    return build_json_response(
        status=HTTPStatus.CREATED,
        payload={"msg": msg}
    )


def expectation_failed_response(msg=None):
    return build_json_response(
        status=HTTPStatus.EXPECTATION_FAILED,
        payload={"msg": msg}
    )

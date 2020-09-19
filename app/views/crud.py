from flask import Blueprint, jsonify

from ..decorators import parse_body
from ..logic.crud import (
    CredentialsSchema,
    TargetSchema,
    check_target_by_id,
    create_credentials,
    create_target,
    delete_credentials_by_id,
    delete_target_by_id,
    edit_credentials_by_id,
    edit_target_by_id,
    get_all_credentials,
    get_all_targets,
    get_credentials_by_id,
    get_target_by_id,
    wakeup_target_by_id,
)

crud = Blueprint('crud', __name__)


@crud.route('/targets/', methods=['GET'])
def get_targets():
    return jsonify(get_all_targets())


@crud.route('/targets/', methods=['POST'])
@parse_body(TargetSchema())
def create_target_(body: dict):
    created = create_target(**body)
    return {'id': created}, 201


@crud.route('/targets/<int:pk>/', methods=['GET'])
def get_target(pk: int):
    return get_target_by_id(pk)


@crud.route('/targets/<int:pk>/', methods=['PUT', 'PATCH'])
@parse_body(TargetSchema())
def update_target(pk: int, body: dict):
    edit_target_by_id(pk, **body)
    return '', 204


@crud.route('/targets/<int:pk>/', methods=['DELETE'])
def delete_target(pk: int):
    delete_target_by_id(pk)
    return '', 204


@crud.route('/targets/<int:pk>/wake/', methods=['POST'])
def wakeup_target(pk: int):
    wakeup_target_by_id(pk)
    return '', 204


@crud.route('/targets/<int:pk>/check/', methods=['POST'])
def check_target(pk: int):
    reached = check_target_by_id(pk)
    return {'reached': reached}


@crud.route('/credentials/', methods=['GET'])
def get_credentials_list():
    return jsonify(get_all_credentials())


@crud.route('/credentials/', methods=['POST'])
@parse_body(CredentialsSchema())
def create_credentials_(body: dict):
    created = create_credentials(**body)
    return {'id': created}, 201


@crud.route('/credentials/<int:pk>/', methods=['GET'])
def get_credentials(pk: int):
    return get_credentials_by_id(pk)


@crud.route('/credentials/<int:pk>/', methods=['PUT', 'PATCH'])
@parse_body(CredentialsSchema())
def update_credentials(pk: int, body: dict):
    edit_credentials_by_id(pk, **body)
    return '', 204


@crud.route('/credentials/<int:pk>/', methods=['DELETE'])
def delete_credentials(pk: int):
    delete_credentials_by_id(pk)
    return '', 204

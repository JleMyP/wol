from typing import List, Optional

from marshmallow import Schema, fields
from peewee import JOIN
from playhouse.flask_utils import get_object_or_404

from ..doc_utils import exclude_parent_attrs
from ..fields import HostField, MacField, PortField
from ..models import Credentials, Target
from .core import check_host, wakeup_host

__all__ = ['create_target', 'get_target_by_id', 'get_all_targets', 'delete_target_by_id',
           'edit_target_by_id', 'wakeup_target_by_id', 'check_target_by_id',
           'create_credentials', 'get_credentials_by_id', 'get_all_credentials',
           'delete_credentials_by_id', 'edit_credentials_by_id',
           'TargetSchema', 'CredentialsSchema']


class CredentialsSchema(Schema):
    """credentials (de)serialization"""
    id = fields.Int(dump_only=True)  # noqa: A003, VNE003
    username = fields.Str()
    password = fields.Str()
    pkey = fields.Str()


class TargetSchema(Schema):
    """target (de)serialization"""
    id = fields.Int(dump_only=True)  # noqa: A003, VNE003
    host = HostField()
    mac = MacField()
    wol_port = PortField()
    credentials = fields.Nested(CredentialsSchema())


def _delete_object(model, id_: int):
    obj = get_object_or_404(model, model.id == id_)
    obj.delete_instance()


def _edit_object_by_id(model, id_: int, **kwargs):
    obj = get_object_or_404(model, model.id == id_)
    edited_fields = []
    for field_name, value in kwargs.items():
        field = getattr(model, field_name)
        edited_fields.append(field)
        setattr(obj, field_name, value)
    obj.save(only=edited_fields)


def create_target(host: Optional[str] = None, mac: Optional[str] = None,
                  wol_port: Optional[int] = None, credentials: Optional[int] = None) -> int:
    target = Target.create(host=host, mac=mac, wol_port=wol_port, credentials=credentials)
    return target.id


def get_target_by_id(id_: int) -> dict:
    query = Target.select(Target, Credentials).join(Credentials, JOIN.LEFT_OUTER)
    target = get_object_or_404(query, Target.id == id_)
    return TargetSchema().dump(target)


def get_all_targets():
    query = Target.select(Target, Credentials).join(Credentials, JOIN.LEFT_OUTER)
    return TargetSchema(many=True).dump(query)


def delete_target_by_id(id_: int):
    _delete_object(Target, id_)


def edit_target_by_id(id_: int, **kwargs):
    _edit_object_by_id(Target, id_, **kwargs)


def wakeup_target_by_id(id_: int):
    target = get_object_or_404(Target, Target.id == id_)
    wakeup_host(target.mac, port=target.wol_port)


def check_target_by_id(id_: int) -> bool:
    target = get_object_or_404(Target, Target.id == id_)
    return check_host(target.host)


def create_credentials(username: str, password: Optional[str] = None,
                       pkey: Optional[str] = None) -> int:
    credentials = Credentials.create(username=username, password=password, pkey=pkey)
    return credentials.id


def get_credentials_by_id(id_: int) -> dict:
    credentials = get_object_or_404(Credentials, Credentials.id == id_)
    return CredentialsSchema().dump(credentials)


def get_all_credentials() -> List[dict]:
    qs = Credentials.select()
    return list(qs.dicts())


def delete_credentials_by_id(id_: int):
    _delete_object(Credentials, id_)


def edit_credentials_by_id(id_: int, **kwargs):
    _edit_object_by_id(Credentials, id_, **kwargs)


for schema in (CredentialsSchema, TargetSchema):
    exclude_parent_attrs(schema)

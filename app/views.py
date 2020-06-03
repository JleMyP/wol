from marshmallow import Schema, fields

from . import app
from .decorators import parse_body
from .fields import (
    HostField,
    IpAddressField,
    MacField,
    PortField,
)
from .logic import (
    RemoteExecError,
    check_host,
    get_cpu_stat,
    reboot_host,
    scan_local_net,
    wakeup_host,
)


class SshActionSchema(Schema):
    host = HostField(required=True)
    port = PortField(missing=22)
    login = fields.String(required=True)
    password = fields.String(required=True)


class WakeupSchema(Schema):
    mac = MacField(required=True)
    ip_address = IpAddressField(missing='255.255.255.255')
    port = PortField(missing=9)


class CheckHostSchema(Schema):
    host = HostField(required=True)


@app.route('/api/check_host/', methods=['POST'])
@parse_body(CheckHostSchema())
def ping(validated_data: dict):
    reached = check_host(**validated_data)
    return {'reached': reached}


@app.route('/api/wake/', methods=['POST'])
@parse_body(WakeupSchema())
def wake(validated_data: dict):
    wakeup_host(**validated_data)
    return '', 204


@app.route('/api/cpu_stat/', methods=['POST'])
@parse_body(SshActionSchema())
def cpu_stat(validated_data: dict):
    try:
        stat = get_cpu_stat(**validated_data, precision=3)
    except RemoteExecError as e:
        return e.as_dict(), 400
    return stat._asdict()


@app.route('/api/scan_net/', methods=['POST'])
def scan_net():
    return {'hosts': scan_local_net()}


@app.route('/api/reboot/', methods=['POST'])
@parse_body(SshActionSchema())
def reboot(validated_data: dict):
    try:
        reboot_host(**validated_data)
    except RemoteExecError as e:
        return e.as_dict(), 400
    return '', 204

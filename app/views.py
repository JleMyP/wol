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
def ping(body: dict):
    """check, if host online."""
    reached = check_host(**body)
    return {'reached': reached}


@app.route('/api/wake/', methods=['POST'])
@parse_body(WakeupSchema())
def wake(body: dict):
    """wakeup host by Wale on lan."""
    wakeup_host(**body)
    return '', 204


@app.route('/api/cpu_stat/', methods=['POST'])
@parse_body(SshActionSchema())
def cpu_stat(body: dict):
    """cpu load of remote host (ssh)."""
    try:
        stat = get_cpu_stat(**body, precision=3)
    except RemoteExecError as e:
        return e.as_dict(), 400
    return stat._asdict()


@app.route('/api/scan_net/', methods=['POST'])
def scan_net():
    """search all hosts in local net."""
    return {'hosts': scan_local_net()}


@app.route('/api/reboot/', methods=['POST'])
@parse_body(SshActionSchema())
def reboot(body: dict):
    """reboot the remote host (ssh)."""
    try:
        reboot_host(**body)
    except RemoteExecError as e:
        return e.as_dict(), 400
    return '', 204

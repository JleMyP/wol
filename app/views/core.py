from flask import Blueprint
from marshmallow import Schema, fields

from ..decorators import parse_body
from ..fields import (
    HostField,
    IpAddressField,
    MacField,
    PortField,
)
from ..logic.core import (
    RemoteExecError,
    check_host,
    get_cpu_stat,
    reboot_host,
    scan_local_net,
    shutdown_host,
    wakeup_host,
)

core = Blueprint('core', __name__)


class SshActionSchema(Schema):
    host = HostField(required=True)
    port = PortField()
    login = fields.String()
    password = fields.String()


class WakeupSchema(Schema):
    mac = MacField(required=True)
    host = IpAddressField(missing='255.255.255.255')
    port = PortField(missing=9)


class CheckHostSchema(Schema):
    host = HostField(required=True)


@core.route('/check_host/', methods=['POST'])
@parse_body(CheckHostSchema())
def ping(body: dict):
    """check, if host online."""
    reached = check_host(**body)
    return {'reached': reached}


@core.route('/wake/', methods=['POST'])
@parse_body(WakeupSchema())
def wake(body: dict):
    """wakeup host by Wake on Lan."""
    wakeup_host(**body)
    return '', 204


@core.route('/cpu_stat/', methods=['POST'])
@parse_body(SshActionSchema())
def cpu_stat(body: dict):
    """cpu load of remote host (ssh)."""
    try:
        stat = get_cpu_stat(**body, precision=3)
    except RemoteExecError as e:
        return e.as_dict(), 400
    return stat._asdict()


@core.route('/reboot/', methods=['POST'])
@parse_body(SshActionSchema())
def reboot(body: dict):
    """reboot the remote host (ssh)."""
    try:
        reboot_host(**body)
    except RemoteExecError as e:
        return e.as_dict(), 400
    return '', 204


@core.route('/shutdown/', methods=['POST'])
@parse_body(SshActionSchema())
def shutdown(body: dict):
    """immediately shutdown the remote host (ssh)."""
    try:
        shutdown_host(**body)
    except RemoteExecError as e:
        return e.as_dict(), 400
    return '', 204


@core.route('/scan_net/', methods=['POST'])
def scan_net():
    """search all hosts in local net."""
    return {'hosts': scan_local_net()}

from flask import jsonify
from marshmallow import Schema, fields

from app import app
from decorators import parse_body
from fields import IpAddressField, HostField, PortField, MacField
from logic import check_host, reboot_host, get_cpu_stat, SshExecError, wakeup_host, scan_local_net


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
    except SshExecError as e:
        return {'out': e.out, 'err': e.err}
    return stat._asdict()


@app.route('/api/scan_net/', methods=['POST'])
def scan_net():
    return jsonify(scan_local_net())


@app.route('/api/reboot/', methods=['POST'])
@parse_body(SshActionSchema())
def reboot(validated_data: dict):
    try:
        reboot_host(**validated_data)
    except SshExecError as e:
        return {'out': e.out, 'err': e.err}
    return '', 204

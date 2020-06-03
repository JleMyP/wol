from marshmallow import ValidationError, fields, validate
from validators import (
    domain,
    ipv4,
    ipv6,
    mac_address,
)

__all__ = ['IpAddressField', 'HostField', 'PortField', 'MacField']


def validate_ip(ip: str):
    for validator in [ipv4, ipv6]:
        if validator(ip) is True:
            break
    else:
        raise ValidationError('is not a valid ip address')


def validate_host(host: str):
    for validator in [ipv4, ipv6, domain]:
        if validator(host) is True:
            break
    else:
        raise ValidationError('is not a valid host')


def validate_mac(mac: str):
    if mac_address(mac) is not True:
        raise ValidationError('is not a valid mac')


def add_validators(name, base, validators):
    def __init__(self, **kwargs):
        _validate = kwargs.pop('validate', [])
        if callable(_validate):
            _validate = [_validate]
        _validate.extend(validators)
        kwargs['validate'] = _validate
        super(base, self).__init__(**kwargs)
    return type(name, (base,), {'__init__': __init__})


IpAddressField = add_validators('IpAddressField', fields.String, [validate_ip])
HostField = add_validators('HostField', fields.String, [validate_host])
PortField = add_validators('PortField', fields.Integer, [validate.Range(min=0, max=2**16 - 1)])
MacField = add_validators('MacField', fields.String, [validate_mac])

"""
Custom fields with validation for marshallow
"""

from typing import (
    Callable,
    List,
    Optional,
    Type,
)

try:
    from fabric.config import Config
except ImportError:
    Config = None

from marshmallow import ValidationError, fields, validate
from validators import (
    domain,
    ipv4,
    ipv6,
    mac_address,
)

from .doc_utils import exclude_parent_attrs

__all__ = ['IpAddressField', 'HostField', 'PortField', 'MacField']


def validate_ip(ip: str) -> None:
    for validator in [ipv4, ipv6]:
        if validator(ip) is True:
            break
    else:
        raise ValidationError(f'"{ip}" is not a valid ip address')


def validate_host(host: str) -> None:
    for validator in [ipv4, ipv6, domain]:
        if validator(host) is True:
            break
    else:
        if not Config:
            return

        patterns = Config().base_ssh_config.get_hostnames()
        # TODO: more complex filter
        known_hosts = [p for p in patterns if '*' not in p]
        known_hosts += ['localhost']
        if host not in known_hosts:
            raise ValidationError(f'"{host}" is not a valid host')


def validate_mac(mac: str) -> None:
    if mac_address(mac) is not True:
        raise ValidationError(f'"{mac}" is not a valid mac')


def add_validators(
        name: str, base: Type[fields.Field],
        validators: List[Callable[[any], None]],
        doc_string: Optional[str] = None,
) -> type:  # TODO: Type[fields.Field]
    """generate schema field by adding validators to existing field.

    :param name: name of a new field.
    :param base: base field.
    :param validators: list of validators.
    :return: a new field with added validators.
    """
    def __init__(self, **kwargs):
        _validate = kwargs.pop('validate', [])
        if callable(_validate):
            _validate = [_validate]
        _validate.extend(validators)
        kwargs['validate'] = _validate
        super(base, self).__init__(**kwargs)  # noqa  # TODO: what's wrong?
    attrs = {'__init__': __init__}
    if doc_string:
        attrs['__doc__'] = doc_string
    return type(name, (base,), attrs)


IpAddressField = add_validators('IpAddressField', fields.String, [validate_ip],
                                'validates IPv4 and IPv6 addresses')
HostField = add_validators('HostField', fields.String, [validate_host],
                           'validates IPv4, IPv6 and domain names')
PortField = add_validators('PortField', fields.Integer, [validate.Range(min=0, max=2**16 - 1)],
                           'validates web port')
MacField = add_validators('MacField', fields.String, [validate_mac],
                          'validates MAC address')

for field in (IpAddressField, HostField, PortField, MacField):
    exclude_parent_attrs(field)

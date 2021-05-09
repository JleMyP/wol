import operator
import os
import subprocess
from dataclasses import dataclass
from numbers import Number
from typing import (
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
)

from wakeonlan import send_magic_packet

try:
    from functools import singledispatchmethod
except ImportError:
    from singledispatchmethod import singledispatchmethod

try:
    import scapy
    import scapy.config
    import scapy.route
    import scapy.utils
    from scapy.layers.l2 import arping
    from scapy.layers.inet import IP, TCP
    from scapy.sendrecv import sr1
except Exception:
    scapy = None

try:
    import fabric
    from paramiko.ssh_exception import NoValidConnectionsError, SSHException
except ImportError:
    fabric = None

from ..doc_utils import exclude_parent_attrs

__all__ = ['CpuStat', 'check_host', 'reboot_host', 'get_cpu_stat', 'wakeup_host', 'RemoteExecError',
           'scan_local_net', 'shutdown_host']

ERROR_NOT_CONNECTED = 0
ERROR_SSH = 1
ERROR_EXEC = 2


class OperableNamedTuple(NamedTuple):
    @singledispatchmethod
    def _do_op(self, other, op):
        raise TypeError

    @_do_op.register(list)
    @_do_op.register(set)
    @_do_op.register(tuple)
    def _do_op_multiple(self, other: Iterable, op: Callable[[Number, Number], Number]):
        return self._make([op(a, b) for a, b in zip(self, other)])

    @_do_op.register(int)
    @_do_op.register(float)
    def _do_op_single(self, other: Number, op: Callable[[Number, Number], Number]):
        return self._make([op(i, other) for i in self])

    def __sub__(self, other):
        return self._do_op(other, operator.sub)

    def __add__(self, other):
        return self._do_op(other, operator.add)

    def __mul__(self, other):
        return self._do_op(other, operator.mul)

    def __truediv__(self, other):
        return self._do_op(other, operator.truediv)

    def __round__(self, num: Optional[int] = None):
        return self._do_op(num, round)


# can't inherit only OperableNamedTuple or OperableNamedTuple with NamedTuple
class CpuStatShortBase(NamedTuple):
    user: float
    system: float
    idle: float
    iowait: float


class CpuStatShort(CpuStatShortBase, OperableNamedTuple):
    pass


class CpuStatBase(NamedTuple):
    """CPU load representation"""
    user: float
    nice: float
    system: float
    idle: float
    iowait: float
    irq: float
    softirq: float
    steal: float
    guest: float
    guest_nice: float

    def short(self) -> CpuStatShort:
        return CpuStatShort(user=self.user + self.nice, system=self.system,
                            idle=self.idle, iowait=self.iowait)  # noqa  # TODO: charm, wtf?


class CpuStat(CpuStatBase, OperableNamedTuple):
    pass


@dataclass
class SshCredentials:
    host: str
    login: Optional[str]
    password: Optional[str]
    port: Optional[int] = 22


class RemoteExecError(Exception):
    """exception while performing remote operation, e.g. reboot"""

    def __init__(self, code: int, reason: str, details: Optional[any] = None):
        self.code = code
        self.reason = reason
        self.details = details

    def as_dict(self) -> dict:
        return {
            'code': self.code,
            'reason': self.reason,
            'details': self.details or {},
        }


@dataclass
class RemoteExecResult:
    stdout: str
    stderr: str
    exit_code: int


if fabric:
    def _remote_exec_command(creds: SshCredentials, command: str, sudo: bool = False) -> RemoteExecResult:
        try:
            with fabric.Connection(creds.host, creds.login, creds.port,
                                   connect_kwargs={'password': creds.password}) as c:
                if sudo:
                    res = c.sudo(command, warn=True, hide=True, password=creds.password)
                else:
                    res = c.run(command, warn=True, hide=True)
        except NoValidConnectionsError:
            raise RemoteExecError(ERROR_NOT_CONNECTED, "can't connect to host")
        except SSHException as e:
            raise RemoteExecError(ERROR_SSH, "ssh exception", vars(e))
        if res.exited:
            raise RemoteExecError(ERROR_EXEC, "can't exec command",
                                  {'out': res.stdout, 'err': res.stderr})
        return RemoteExecResult(stdout=res.stdout, stderr=res.stderr, exit_code=res.exited)
else:
    def _remote_exec_command(*args, **kwargs):
        raise NotImplementedError


def get_cpu_stat(creds: SshCredentials, precision: Optional[int] = None) -> CpuStat:
    # TODO: add memory information
    cmd = 'head -1 /proc/stat && sleep 1 > /dev/null && head -1 /proc/stat'
    res = _remote_exec_command(creds, cmd)
    l1, l2, *_ = res.stdout.split('\n')
    stat = _get_delta_from_str(l1, l2)
    if precision:
        stat = round(stat, precision)
    return stat


def _get_delta_from_str(s1: str, s2: str) -> CpuStat:
    measure1 = CpuStat(*map(int, s1.split()[1:]))
    measure2 = CpuStat(*map(int, s2.split()[1:]))
    diff = measure2 - measure1
    full = sum(measure2) - sum(measure1)
    return diff / full * 100


def _can_use_scapy() -> bool:
    return os.geteuid() == 0 and scapy is not None


def check_host(host: str, port: Optional[int] = 80) -> bool:
    if _can_use_scapy():
        return check_host_scapy(host, port=port)
    return check_host_ping(host)


def check_host_scapy(host: str, port: Optional[int] = 80) -> bool:
    """check by SYN/ACK to specified port."""
    packet = IP(dst=host) / TCP(dport=port or 80)
    response = sr1(packet, timeout=15)
    return response is not None


def check_host_ping(host: str) -> bool:
    cmd = ['ping', '-c', '1', '-W', '2', host]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    proc.communicate()
    return proc.returncode == 0


def wakeup_host(mac: str, host: str = '255.255.255.255', port: int = 9) -> None:
    # scapy:
    #     from scapy.sendrecv import send
    #     from scapy.layers.inet import IP, UDP
    #     magic = bytes.fromhex(mac.replace(':', '')
    #     start = bytes.fromhex('FF')*6
    #     packet = IP(dst=host) / UDP(dport=port) / (start + magic*16)
    #     send(packet)
    send_magic_packet(mac, ip_address=host, port=port)


def reboot_host(creds: SshCredentials, sudo: bool = True) -> None:
    _remote_exec_command(creds, 'reboot', sudo)


def shutdown_host(creds: SshCredentials, sudo: bool = True) -> None:
    _remote_exec_command(creds, 'shutdown now', sudo)


def scan_local_net(net: Optional[str] = None) -> List[Dict[str, str]]:
    """get hosts (ip, mac) from local net by ARP protocol."""
    # TODO: select network interface w/o mask - get mask from adapter
    # TODO: select network interface by unique prefix
    # TODO: error, if net is not provided and multiple interfaces found
    if not _can_use_scapy():
        raise NotImplementedError

    if not net:
        net = get_net()
    ans, _ = arping(net)
    hosts = [{'ip': r.psrc, 'mac': r.hwsrc} for _, r in ans.res]
    return hosts


def get_net() -> str:
    """find network interface/mask, that has access to the Internet."""
    # TODO: need rework
    #  can find multiple interfaces
    for network, netmask, _, interface, address, _ in scapy.config.conf.route.routes:
        if network == 0 or interface == 'lo' or address in ('127.0.0.1', '0.0.0.0'):  # noqa: S104
            continue
        if netmask <= 0 or netmask == 0xFFFFFFFF:
            continue
        if interface.startswith('docker') or interface.startswith('br-'):
            continue
        addr_num = scapy.utils.atol(address)
        if addr_num & netmask != network:
            continue
        net = scapy.utils.ltoa(network)
        mask = bin(netmask).count('1')
        return f'{net}/{mask}'


exclude_parent_attrs(CpuStat)
exclude_parent_attrs(RemoteExecError)

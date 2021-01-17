import operator
import os
import subprocess
from numbers import Number
from typing import (
    Callable,
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
           'scan_local_net']

ERROR_NOT_CONNECTED = 0
ERROR_SSH = 1
ERROR_EXEC = 2


class CpuStatShortBase(NamedTuple):
    user: float
    system: float
    idle: float
    iowait: float


class CpuStatBase(NamedTuple):
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


class BaseOps(NamedTuple):
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


class CpuStat(CpuStatBase, BaseOps):
    """CPU load representation"""
    def short(self):
        return CpuStatShort(user=self.user + self.nice, system=self.system,
                            idle=self.idle, iowait=self.iowait)  # noqa  # TODO: charm, wtf?


class CpuStatShort(CpuStatShortBase, BaseOps):
    pass


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


if fabric:
    def remote_exec_command(command: str, host: str, login: str, password: str,
                            port: int = 22) -> dict:
        try:
            with fabric.Connection(host, login, port, connect_kwargs={'password': password}) as c:
                res = c.run(command, warn=True)
        except NoValidConnectionsError:
            raise RemoteExecError(ERROR_NOT_CONNECTED, "can't connect to host")
        except SSHException:
            raise RemoteExecError(ERROR_SSH, 'ssh exception')
        if res.exited:
            raise RemoteExecError(ERROR_EXEC, "can't exec command",
                                  {'out': res.stdout, 'err': res.stderr})
        as_dict = vars(res)
        as_dict.pop('connection')
        return as_dict
else:
    def remote_exec_command(*args, **kwargs):
        raise NotImplementedError


def get_cpu_stat(host: str, login: str, password: str, port: int = 22,
                 precision: Optional[int] = None) -> CpuStat:
    # TODO: describe the algorithm
    cmd = 'head -1 /proc/stat && sleep 1 1>/dev/null && head -1 /proc/stat'
    res = remote_exec_command(cmd, host, login, password, port)
    l1, l2, *_ = res['stdout'].split('\n')
    stat = get_delta_from_str(l1, l2)
    if precision:
        stat = round(stat, precision)
    return stat


def get_delta_from_str(s1: str, s2: str) -> CpuStat:
    measure1 = CpuStat(*map(int, s1.split()[1:]))
    measure2 = CpuStat(*map(int, s2.split()[1:]))
    diff = measure2 - measure1
    full = sum(measure2) - sum(measure1)
    return diff / full * 100


def can_use_scapy() -> bool:
    return os.geteuid() == 0 and scapy is not None


def check_host(host: str) -> bool:
    if can_use_scapy():
        return check_host_scapy(host)
    return check_host_ping(host)


def check_host_scapy(host: str) -> bool:
    """check by SYN/ACK to 80 port."""
    packet = IP(dst=host) / TCP()
    print(packet)
    response = sr1(packet, timeout=15)
    return response is not None


def check_host_ping(host: str) -> bool:
    cmd = ['ping', '-c', '1', '-W', '2', host]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    proc.communicate()
    return proc.returncode == 0


def wakeup_host(mac: str, host: str = '255.255.255.255', port: int = 9):
    # scapy:
    #     from scapy.sendrecv import send
    #     from scapy.layers.inet import IP, UDP
    #     magic = bytes.fromhex(mac.replace(':', '')
    #     start = bytes.fromhex('FF')*6
    #     packet = IP(dst=host) / UDP(dport=port) / (start + magic*16)
    #     send(packet)
    send_magic_packet(mac, ip_address=host, port=port)


def reboot_host(host: str, login: str, password: str, port: int = 22):
    remote_exec_command('reboot', host, login, password, port)


def scan_local_net() -> List[str]:
    """get hosts from local net by ARP protocol."""
    if not can_use_scapy():
        raise NotImplementedError

    net = get_net()
    ans, _ = arping(net)
    hosts = [r.psrc for _, r in ans.res]
    return hosts


def get_net() -> str:
    """find network interface/mask, that has access to the Internet."""
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

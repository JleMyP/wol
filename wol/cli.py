#!/bin/env python3
"""
entrypoint for launching command line interface.
"""

import json
from collections import OrderedDict
from contextlib import contextmanager
from inspect import Parameter, signature
from typing import Callable, Optional

import typer
from marshmallow import ValidationError
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import JsonLexer

from .fields import validate_host as _validate_host
from .fields import validate_mac as _validate_mac
from .logic import core
from .logic.core import SshCredentials

app = typer.Typer(help="Wake On Lan and some useful stuff")
global_opts = {
    'vetbose': False,
}


def validate(ctx: typer.Context, validator: Callable, value: any) -> any:
    """wrapper, that ignore validation at completion search"""
    if ctx.resilient_parsing:
        return

    try:
        validator(value)
    except ValidationError as e:
        raise typer.BadParameter('; '.join(e.messages))

    return value


def validate_host(ctx: typer.Context, host: str) -> Optional[str]:
    return validate(ctx, _validate_host, host)


def validate_mac(ctx: typer.Context, mac: str) -> Optional[str]:
    return validate(ctx, _validate_mac, mac)


@contextmanager
def catch_remote_error(verbose: bool) -> None:
    """unified display ssh errors"""
    try:
        yield
    except NotImplementedError:
        err = typer.style("can't use remote execution", fg=typer.colors.RED)
        typer.echo(err + "\nfabric is installed?", err=True)
        raise typer.Exit(code=1)
    except core.RemoteExecError as e:
        err = typer.style("can't exec command host: ", fg=typer.colors.RED)
        err += e.reason
        if verbose and e.details:
            fmt = highlight(json.dumps(e.details, indent=4), JsonLexer(), TerminalFormatter())
            err += '\n' + fmt
        typer.echo(err, err=True)
        raise typer.Exit(code=1)


def replace_ssh_args(func) -> Callable:
    """add ssh parameters to command and pass it to the target function as dataclass"""
    def decorated(
            # TODO: path to ssh config and disabling it
            host: str = typer.Argument(..., callback=validate_host,
                                       help="remote host. it can be ip, hostname"
                                            " and alias from ssh config"),
            login: Optional[str] = typer.Option(None, help="ssh username. default - current user"
                                                           " or from ssh config"),
            password: Optional[str] = typer.Option(None, help="ssh password. default - "
                                                              "none or from ssh config"),
            port: Optional[int] = typer.Option(None, '--port', '-p', min=1, max=2**16 - 1,
                                               help="ssh port. default - 22 or from ssh config"),
            **kwargs,
    ):
        kwargs[param_name] = SshCredentials(host=host, port=port, login=login, password=password)
        return func(**kwargs)

    param_name = [k for k, v in func.__annotations__.items() if v is SshCredentials][0]
    fsig = signature(func)
    fparams = OrderedDict(**fsig.parameters)
    fparams.pop(param_name)
    dparams = signature(decorated).parameters
    dparams = OrderedDict(**{k: v for k, v in dparams.items() if v.kind != Parameter.VAR_KEYWORD})
    fsig._parameters = OrderedDict(**dparams, **fparams)
    decorated.__signature__ = fsig
    decorated.__annotations__.update(**{k: v for k, v in func.__annotations__.items()
                                        if k != param_name})
    # functools.wraps loses the annotations
    decorated.__name__ = func.__name__
    decorated.__doc__ = func.__doc__
    return decorated


@app.callback()
def global_callback(
        verbose: bool = typer.Option(False, '--verbose', '-v', help="more detailed output"),
) -> None:
    global_opts['verbose'] = verbose


@app.command()
def check(
        host: str = typer.Argument(..., callback=validate_host, help="remote host. ip or hostname"),
) -> None:
    """check if host is online (SYN/ACK to 80 port or ping)"""
    result = core.check_host(host)
    if result:
        typer.secho("reached", fg=typer.colors.GREEN)
    else:
        typer.secho("not reached", fg=typer.colors.RED)
        raise typer.Exit(code=1)


@app.command()
def wake(
        mac: str = typer.Argument(..., callback=validate_mac, help="MAC address of a remote host"),
        host: str = typer.Option('255.255.255.255', '--host', '-h',
                                 callback=validate_host, help="ip addr for packet destination"),
        port: int = typer.Option(9, '--port', '-p', min=1, max=2**16 - 1, help="WOL port"),
) -> None:
    """wake up the host"""
    core.wakeup_host(mac, host, port)
    typer.echo("✨ Magic ✨ packet sent")


@app.command()
@replace_ssh_args
def reboot(
        creds: SshCredentials,
) -> None:
    """reboot a remote host (ssh)"""
    with catch_remote_error(global_opts['verbose']):
        core.reboot_host(creds)

    typer.secho("reboot started", fg=typer.colors.GREEN)


@app.command()
@replace_ssh_args
def shutdown(
        creds: SshCredentials,
) -> None:
    """immediately shutdown a remote host (ssh)"""
    with catch_remote_error(global_opts['verbose']):
        core.shutdown_host(creds)

    typer.secho("shutdown success", fg=typer.colors.GREEN)


@app.command()
@replace_ssh_args
def stats(
        creds: SshCredentials,
        precision: Optional[int] = typer.Option(None, help="count of digits after point"),
) -> None:
    """get CPU stats of a remote host (ssh)"""
    with catch_remote_error(global_opts['verbose']):
        result = core.get_cpu_stat(creds, precision)

    fmt = json.dumps(result._asdict(), indent=4)
    fmt = highlight(fmt, JsonLexer(), TerminalFormatter())
    typer.echo(fmt)


@app.command()
def scan() -> None:
    """scan local net by ARP protocol"""
    try:
        results = core.scan_local_net()
    except NotImplementedError:
        err = typer.style("can't use scapy", fg=typer.colors.RED)
        typer.echo(err + "\nit is installed and user is root?", err=True)
        raise typer.Exit(code=1)

    if results:
        typer.echo("results:\n" + '\n'.join(f'{pair["ip"]} \t| {pair["mac"]}' for pair in results))
    else:
        typer.echo("no results")


if __name__ == '__main__':
    app()

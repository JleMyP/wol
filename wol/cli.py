#!/bin/env python3
"""
entrypoint for launching command line interface.
"""

import functools
import json
from collections import OrderedDict
from contextlib import contextmanager
from inspect import Parameter, signature
from pathlib import Path
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

try:
    from .logic import crud
    from . import models
except ImportError:
    crud = False

app = typer.Typer(help="Wake On Lan and some useful stuff")


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


def validate_optional_mac(ctx: typer.Context, mac: Optional[str]) -> Optional[str]:
    if not mac:
        return
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
            # TODO: connect timeout
            **kwargs,
    ):
        kwargs[param_name] = SshCredentials(host=host, port=port, login=login, password=password)
        return func(**kwargs)

    # merge signatures, except complex ssh creds
    fsig = signature(func)
    param_name = [k for k, v in fsig.parameters.items()
                  if v.annotation is SshCredentials][0]
    fparams = {k: v for k, v in fsig.parameters.items()
                 if v.annotation is not SshCredentials}
    dparams = signature(decorated).parameters
    # drop "kwargs"
    dparams = {k: v for k, v in dparams.items()
                 if v.kind != Parameter.VAR_KEYWORD}
    fsig._parameters = OrderedDict(**fparams, **dparams)

    # rewrite signature and type hints
    decorated = functools.wraps(func)(decorated)
    decorated.__signature__ = fsig
    # merge annotations, except complex ssh creds
    decorated.__annotations__.update(**{k: v for k, v in func.__annotations__.items()
                                        if v is not SshCredentials})
    return decorated


def require_db(func) -> Callable:
    def throw(*args, **kwargs) -> None:
        typer.secho("database support not enabled", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1)

    if not crud:
        return throw

    @functools.wraps(func, assigned=functools.WRAPPER_ASSIGNMENTS + ('__signature',))
    def decorated(*args, **kwargs) -> any:
        models.setup_connection(kwargs['ctx'].meta['database_url'])
        models.init_db()
        return func(*args, **kwargs)

    return decorated


@app.callback()
def global_callback(
        ctx: typer.Context,
        verbose: bool = typer.Option(False, '--verbose', '-v', help="more detailed output"),
        config_file: Optional[Path] = typer.Option(None, '--config-file',
                                                   help="path to config file"),
        database_url: str = typer.Option('sqlite:///sqlite.db', '--db',
                                         help="database url", envvar='DATABASE_URL'),
) -> None:
    ctx.meta['verbose'] = verbose

    if config_file:
        ...  # todo: read: db url, ssh timeout

    ctx.meta['database_url'] = database_url


@app.command()
def check(
        host: str = typer.Argument(..., callback=validate_host, help="remote host. ip or hostname"),
) -> None:
    """check if host is online (SYN/ACK to 80 port or ping)"""
    result = core.check_host(host)
    if result:
        typer.secho("reached", fg=typer.colors.GREEN)
    else:
        typer.secho("not reached", fg=typer.colors.RED, err=True)
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
        ctx: typer.Context,
        creds: SshCredentials,
) -> None:
    """immediately shutdown a remote host (ssh)"""
    with catch_remote_error(ctx.meta['verbose']):
        core.shutdown_host(creds)

    typer.secho("shutdown success", fg=typer.colors.GREEN)


@app.command()
@replace_ssh_args
def stats(
        ctx: typer.Context,
        creds: SshCredentials,
        precision: Optional[int] = typer.Option(None, help="count of digits after point"),
) -> None:
    """get CPU stats of a remote host (ssh)"""
    with catch_remote_error(ctx.meta['verbose']):
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


@app.command()
@require_db
@replace_ssh_args
def add_target(
        ctx: typer.Context,
        creds: SshCredentials,
        name: str = typer.Argument(..., help="host alias"),
        mac: Optional[str] = typer.Option(None, callback=validate_optional_mac,
                                          help="MAC address of a remote host"),
        wol_port: int = typer.Option(9, '--wol-port', '-w', min=1, max=2**16 - 1, help="WOL port"),
) -> None:
    created = crud.create_target(
        name=name,
        host=creds.host,
        mac=mac,
        wol_port=wol_port,
    )
    fmt = json.dumps(created, indent=4)
    fmt = highlight(fmt, JsonLexer(), TerminalFormatter())
    typer.echo(fmt)


if __name__ == '__main__':
    app()

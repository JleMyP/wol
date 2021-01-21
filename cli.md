# `./cli.py`

Wake On Lan and some useful stuff

**Usage**:

```console
$ ./cli.py [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `-v, --verbose`: more detailed output  [default: False]
* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `check`: check if host is online (SYN/ACK to 80 port...
* `reboot`: reboot a remote host (ssh)
* `scan`: scan local net by ARP protocol
* `shutdown`: immediately shutdown a remote host (ssh)
* `stats`: get CPU stats of a remote host (ssh)
* `wake`: wake up the host

## `./cli.py check`

check if host is online (SYN/ACK to 80 port or ping)

**Usage**:

```console
$ ./cli.py check [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. ip or hostname  [required]

**Options**:

* `--help`: Show this message and exit.

## `./cli.py reboot`

reboot a remote host (ssh)

**Usage**:

```console
$ ./cli.py reboot [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. it can be ip, hostname and alias from ssh config  [required]

**Options**:

* `--login TEXT`: ssh username. default - current user or from ssh config
* `--password TEXT`: ssh password. default - none or from ssh config
* `-p, --port INTEGER RANGE`: ssh port. default - 22 or from ssh config
* `--help`: Show this message and exit.

## `./cli.py scan`

scan local net by ARP protocol

**Usage**:

```console
$ ./cli.py scan [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `./cli.py shutdown`

immediately shutdown a remote host (ssh)

**Usage**:

```console
$ ./cli.py shutdown [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. it can be ip, hostname and alias from ssh config  [required]

**Options**:

* `--login TEXT`: ssh username. default - current user or from ssh config
* `--password TEXT`: ssh password. default - none or from ssh config
* `-p, --port INTEGER RANGE`: ssh port. default - 22 or from ssh config
* `--help`: Show this message and exit.

## `./cli.py stats`

get CPU stats of a remote host (ssh)

**Usage**:

```console
$ ./cli.py stats [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. it can be ip, hostname and alias from ssh config  [required]

**Options**:

* `--login TEXT`: ssh username. default - current user or from ssh config
* `--password TEXT`: ssh password. default - none or from ssh config
* `-p, --port INTEGER RANGE`: ssh port. default - 22 or from ssh config
* `--precision INTEGER`: count of numers after point
* `--help`: Show this message and exit.

## `./cli.py wake`

wake up the host

**Usage**:

```console
$ ./cli.py wake [OPTIONS] MAC
```

**Arguments**:

* `MAC`: MAC address of a remote host  [required]

**Options**:

* `-h, --host TEXT`: ip addr for packet destination  [default: 255.255.255.255]
* `-p, --port INTEGER RANGE`: WOL port  [default: 9]
* `--help`: Show this message and exit.

# `wol-cli`

Wake On Lan and some useful stuff

**Usage**:

```console
$ wol-cli [OPTIONS] COMMAND [ARGS]...
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

## `wol-cli check`

check if host is online (SYN/ACK to 80 port or ping)

**Usage**:

```console
$ wol-cli check [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. ip or hostname  [required]

**Options**:

* `--help`: Show this message and exit.

## `wol-cli reboot`

reboot a remote host (ssh)

**Usage**:

```console
$ wol-cli reboot [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. it can be ip, hostname and alias from ssh config  [required]

**Options**:

* `--login TEXT`: ssh username. default - current user or from ssh config
* `--password TEXT`: ssh password. default - none or from ssh config
* `-p, --port INTEGER RANGE`: ssh port. default - 22 or from ssh config
* `--help`: Show this message and exit.

## `wol-cli scan`

scan local net by ARP protocol

**Usage**:

```console
$ wol-cli scan [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `wol-cli shutdown`

immediately shutdown a remote host (ssh)

**Usage**:

```console
$ wol-cli shutdown [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. it can be ip, hostname and alias from ssh config  [required]

**Options**:

* `--login TEXT`: ssh username. default - current user or from ssh config
* `--password TEXT`: ssh password. default - none or from ssh config
* `-p, --port INTEGER RANGE`: ssh port. default - 22 or from ssh config
* `--help`: Show this message and exit.

## `wol-cli stats`

get CPU stats of a remote host (ssh)

**Usage**:

```console
$ wol-cli stats [OPTIONS] HOST
```

**Arguments**:

* `HOST`: remote host. it can be ip, hostname and alias from ssh config  [required]

**Options**:

* `--login TEXT`: ssh username. default - current user or from ssh config
* `--password TEXT`: ssh password. default - none or from ssh config
* `-p, --port INTEGER RANGE`: ssh port. default - 22 or from ssh config
* `--precision INTEGER`: count of numers after point
* `--help`: Show this message and exit.

## `wol-cli wake`

wake up the host

**Usage**:

```console
$ wol-cli wake [OPTIONS] MAC
```

**Arguments**:

* `MAC`: MAC address of a remote host  [required]

**Options**:

* `-h, --host TEXT`: ip addr for packet destination  [default: 255.255.255.255]
* `-p, --port INTEGER RANGE`: WOL port  [default: 9]
* `--help`: Show this message and exit.

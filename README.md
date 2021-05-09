# wol
Wake on Lan and some useful stuff as web service.

[![License: WTFPL](https://img.shields.io/badge/License-WTFPL-brightgreen.svg)](http://www.wtfpl.net/about/)
![code factor](https://img.shields.io/codefactor/grade/github/JleMyP/wol)
![cc maintainability](https://img.shields.io/codeclimate/maintainability-percentage/JleMyP/wol)
![cc issues](https://img.shields.io/codeclimate/issues/JleMyP/wol)

![ci](https://img.shields.io/github/workflow/status/JleMyP/wol/ci/master?label=lint)
![docs](https://img.shields.io/github/workflow/status/JleMyP/wol/release/master?label=build)
![release](https://img.shields.io/github/v/release/JleMyP/wol)

## install

```shell
pip install git+https://github.com/JleMyP/wol.git#egg=wol[all]
```

for using as cli tool, i recommend use pipx

```shell
pipx install git+https://github.com/JleMyP/wol.git#egg=wol[cli,ssh,scapy]
```

## launch dev web server

```shell
wol-dev-server
```

to get command-line arguments type `wol-dev-server -h`.

**arguments**  
* `--bind`, `-b` - listen interface address. default - 127.0.0.1;  
* `--port`, `-p` - listen port. default - 5000;  
* `--debug`, `-d` - run in debug mode. default - false;  
* `--no-db` - do not use database and disable CRUD api.


arguments also can be passed through env vars prefixed by `WOL_`,
example - `WOL_PORT=3000 python -m wol.wsgi`.  


## more seriously launch

```shell
gunicorn --access-logfile - 'wol.wsgi:create_app()'
```

## docker launch

```shell
docker run --rm -ti -p 5000:5000 ghcr.io/jlemyp/wol
```

or for use syn/ack tcp packets instead of ping for checking host:

```shell
docker run --rm -u root -p 5000:5000 ghcr.io/jlemyp/wol
```

port can be passed at the build stage - `--build-arg PORT=8000`,
or at the launch stage - `-e PORT=8000`.  
default user has no root permissions, so the port can't be less than 1024,
or you can launch the container with root user - `-u root -e PORT=80`.  
other configurations can be passed wia `GUNICORN_CMD_ARGS` variable.


## usage

[api doc](docs/api.html)  
[cli doc](cli/)


## todo

functionality:

* ssh pkey
* access control
  * jwt
* browsable interface
* configuration
  * sentry dsn
  * userless mode
* sync names: host, hostname, address, login, username, etc
* validate model filling in per model actions
* replace configparser by typer
* extend per model actions
* mass core operations
* mass per model operations
* add hosts from scanning net

operability:

* in-app openapi doc
* healthcheck
  * disable ht logs
* sentry
* tests
  * ci

# wol
wake on lan and some useful stuff as web service.

## install

```bash
pip install poetry
poetry install
```

## dev launch

```bash
poetry run python main.py
```

to get command-line arguments type `python main.py -h`.  

**arguments**  
* `--bind`, `-b` - listen interface address. default - 127.0.0.1;  
* `--port`, `-p` - listen port. default - 5000;  
* `--debug`, `-d` - run in debug mode. default - false;  
* `--no-db` - do not use database and disable CRUD api.  


arguments also can be passed through env vars prefixed by `WOL_`,
example - `WOL_PORT=3000 python main.py`.  


## more seriously launch

```
poetry run gunicorn --access-logfile - app:app
```

## docker launch

```bash
docker build -t wol -f docker/Dockerfile-prod .
docker run --rm -ti -p 5000:5000 wol
```

port can be passed at the build stage - `--build-arg PORT=8000`,
or at the launch stage - `-e PORT=8000`.  
default user has no root permissions, so the port can't be less than 1024,
or you can launch the container with root user - `-u root -e PORT=80`.  
other configurations can be passed wia `GUNICORN_CMD_ARGS` variable.


## usage

**api**  
[api](docs/api.html)  

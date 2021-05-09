#!/usr/bin/env python3
"""
entrypoint for launching dev server.
"""

import sys

import logging

from environs import Env
from flask import Flask, Response, jsonify
from marshmallow import ValidationError

from configargparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from .views import core

try:
    from . import models
except ImportError:
    models = None
else:
    from .views import crud, pages


def create_app(no_db: bool = False):
    env = Env()
    env.read_env()

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(sys.stdout))

    app = Flask(__name__)
    app.register_blueprint(core, url_prefix='/api')

    with env.prefixed('WOL_'):
        logger.setLevel(env.log_level('LOG_LEVEL', logging.DEBUG))
        if not env('NO_DB', False) and not no_db and models:  # TODO: shit
            app.config['DATABASE'] = env.str('DATABASE_URL', 'postgres://postgres@localhost:5432/wol')
            models.db.init_app(app)
            app.register_blueprint(crud, url_prefix='/api')
            app.register_blueprint(pages)

    @app.errorhandler(ValidationError)
    def handle_validation(error: ValidationError):
        response = jsonify(error.messages)
        response.status_code = 400
        return response

    @app.errorhandler(NotImplementedError)
    def handle_not_implemented(_error: NotImplementedError):
        return Response(status=501)

    return app

    # TODO: catch 404?


def dev_server():
    parser = ArgumentParser(
        auto_env_var_prefix='WOL_',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--bind', '-b', default='127.0.0.1', help="ip address to listen")
    parser.add_argument('--port', '-p', default=5000, help="port to listen")
    parser.add_argument('--debug', '-d', action='store_true', default=False,
                        help="run in debug mode")
    parser.add_argument('--no-db', action='store_true', default=False,
                        help="do not use database and disable CRUD api")
    parser.add_argument('command', choices=('run', 'initdb'), nargs='?', default='run')

    args = parser.parse_args()
    app = create_app(no_db=args.no_db)

    if args.command == 'run':
        app.run(host=args.bind, port=args.port, debug=args.debug)
    elif args.command == 'initdb':
        if args.no_db:
            print("incompatible command and \"--no-db\" argument")
            sys.exit(1)
        elif not models:
            print("database deps is not installed (extra \"db\"")
            sys.exit(1)
        else:
            models.init_db()
            print("db initialized")


if __name__ == '__main__':
    dev_server()

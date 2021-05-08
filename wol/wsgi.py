#!/usr/bin/env python3
"""
входная точка для запуска dev сервера.
"""

import sys

from configargparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from .app import create_app, models


def dev_server():
    parser = ArgumentParser(
        auto_env_var_prefix='WOL_',
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument('--bind', '-b', default='127.0.0.1', help='ip address to listen')
    parser.add_argument('--port', '-p', default=5000, help='port to listen')
    parser.add_argument('--debug', '-d', action='store_true', default=False,
                        help='run in debug mode')
    parser.add_argument('--no-db', action='store_true', default=False,
                        help='do not use database and disable CRUD api')
    parser.add_argument('command', choices=('run', 'initdb'), nargs='?', default='run')

    args = parser.parse_args()
    app = create_app(no_db=args.no_db)

    if args.command == 'run':
        app.run(host=args.bind, port=args.port, debug=args.debug)
    elif args.command == 'initdb':
        if args.no_db:
            print('incompatible command and "--no-db" argument')
            sys.exit(1)
        else:
            models.init_db()
            print('db initualized')


if __name__ == '__main__':
    dev_server()

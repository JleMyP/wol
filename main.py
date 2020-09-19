#!/usr/bin/env python3
"""
входная точка для запуска dev сервера.
"""

from configargparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from app import create_app


if __name__ == '__main__':
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

    args = parser.parse_args()
    app = create_app(no_db=args.no_db)
    app.run(host=args.bind, port=args.port, debug=args.debug)
else:
    app = create_app()

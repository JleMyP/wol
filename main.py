#!/usr/bin/env python3
"""
входная точка для запуска dev сервера.
"""


from configargparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from app import app, views  # noqa

parser = ArgumentParser(
    auto_env_var_prefix='WOL_',
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument('--bind', '-b', default='127.0.0.1', help='ip address to listen')
parser.add_argument('--port', '-p', default=5000, help='port to listen')
parser.add_argument('--debug', '-d', action='store_true', default=False, help='run in debug mode')

if __name__ == '__main__':
    args = parser.parse_args()
    app.run(host=args.bind, port=args.port, debug=args.debug)

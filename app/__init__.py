import logging
from sys import stdout

from environs import Env
from flask import Flask, Response, jsonify
from marshmallow import ValidationError

from .views import core

try:
    from .models import db
except ImportError:
    db = None

if db:
    from .views import crud, pages


def create_app(no_db: bool = False):
    env = Env()
    env.read_env()

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(stdout))

    app = Flask(__name__)
    app.register_blueprint(core, url_prefix='/api')

    with env.prefixed('WOL_'):
        logger.setLevel(env.log_level('LOG_LEVEL', logging.DEBUG))
        # TODO: треш
        if not env('NO_DB', False) and not no_db and db:
            app.config['DATABASE'] = env.str('DATABASE_URL', 'postgres://postgres@localhost:5432/wol')
            db.init_app(app)
            app.register_blueprint(crud, url_prefix='/api')
            app.register_blueprint(pages)

    @app.errorhandler(ValidationError)
    def handle_validation(error: ValidationError):
        response = jsonify(error.messages)
        response.status_code = 400
        return response

    @app.errorhandler(NotImplementedError)
    def handle_not_implemented(error: NotImplementedError):
        return Response(status=501)

    return app

    # TODO: ловить 404?

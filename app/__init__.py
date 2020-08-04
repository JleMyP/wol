import logging
from sys import stdout

from environs import Env
from flask import Flask, Response, jsonify
from marshmallow import ValidationError

from .models import db
from .views import api


def create_app():
    env = Env()
    env.read_env()

    logger = logging.getLogger(__name__)
    logger.addHandler(logging.StreamHandler(stdout))

    app = Flask(__name__)
    app.register_blueprint(api, url_prefix='/api')

    with env.prefixed('WOL_'):
        logger.setLevel(env.log_level('LOG_LEVEL', logging.DEBUG))
        app.config['DATABASE'] = env.str('DATABASE', 'postgres://postgres@localhost:5432/wol')
        db.init_app(app)


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

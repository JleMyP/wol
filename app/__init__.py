import logging
from sys import stdout

from flask import Flask, Response, jsonify
from marshmallow import ValidationError

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
log.addHandler(logging.StreamHandler(stdout))
# TODO: шо это

app = Flask(__name__)

# TODO: env
app.config['DATABASE'] = 'postgres://postgres@localhost:5432/wol'


@app.errorhandler(ValidationError)
def handle_validation(error: ValidationError):
    response = jsonify(error.messages)
    response.status_code = 400
    return response


@app.errorhandler(NotImplementedError)
def handle_not_implemented(error: NotImplementedError):
    return Response(status=501)


# TODO: ловить 404?

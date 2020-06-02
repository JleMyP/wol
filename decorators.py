from functools import wraps

from flask import request
from marshmallow import Schema

__all__ = ['parse_body', 'parse_query']


def parse_body(schema: Schema):
    def decorator(func):
        @wraps(func)
        def wrapped():
            data = schema.load(request.get_json())
            return func(data)
        return wrapped
    return decorator


def parse_query(schema: Schema):
    def decorator(func):
        @wraps(func)
        def wrapped():
            data = schema.load(request.args)
            return func(data)
        return wrapped
    return decorator

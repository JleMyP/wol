from functools import wraps
from typing import Callable

from flask import request
from marshmallow import Schema

__all__ = ['parse_body', 'parse_query']

DECORATOR_TYPE = Callable[[Callable], Callable]


def parse_body(schema: Schema) -> DECORATOR_TYPE:
    """parse the request json body according to the specified scheme."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(*args, **kwargs):
            data = schema.load(request.get_json())
            return func(*args, **kwargs, body=data)
        return wrapped
    return decorator


def parse_query(schema: Schema) -> DECORATOR_TYPE:
    """parse the request query parameters according to the specified scheme."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapped(*args, **kwargs):
            data = schema.load(request.args)
            return func(*args, **kwargs, query=data)
        return wrapped
    return decorator

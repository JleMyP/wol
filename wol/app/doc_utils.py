import inspect


def exclude_parent_attrs(klass, skip=()):
    module = inspect.getmodule(klass)
    if not hasattr(module, '__pdoc__'):
        module.__pdoc__ = {}
    parent_fields = [field for parent in klass.__bases__
                     for field in dir(parent)
                     if not field.startswith('_') and field not in skip]
    for field in parent_fields:
        module.__pdoc__[f'{klass.__name__}.{field}'] = None

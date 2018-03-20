from collections import namedtuple

def tupleclass(*fields):
    def decorator(klass):
        struct = namedtuple(klass.__name__, tuple(fields))
        return type(klass.__name__, (*klass.__bases__, struct), dict(vars(klass)))
    return decorator

def caseclass(*fields):
    def decorator(klass):
        return type(klass.__name__, (struct, *klass.__bases__), dict(vars(klass)))
    return decorator

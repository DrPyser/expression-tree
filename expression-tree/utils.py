from collections import namedtuple

def tupleclass(*fields):
    def decorator(klass):
        struct = namedtuple(klass.__name__, tuple(fields))
        return type(klass.__name__, (struct, *klass.__bases__), dict(vars(klass)))
    

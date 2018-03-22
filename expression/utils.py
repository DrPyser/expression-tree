from collections import namedtuple
from typing import Optional, Mapping, List

def tupleclass(*fields):
    def decorator(klass):
        struct = namedtuple(klass.__name__, tuple(fields))
        return type(klass.__name__, (*klass.__bases__, struct), dict(vars(klass)))
    return decorator


def resolver(parameters: List[str], defaults: Optional[Mapping]=None):
    """
    Creates a function that resolves its positional 
    and keyword arguments against a list of parameters,
    returning a mapping from parameter to argument value.
    :param parameters: parameters to resolve against
    :param defaults: default values for parameters
    """
    defaults = defaults or {}
    def resolve(*args, **kwargs):
        resolved = dict(zip(parameters, args)) # resolved positionals
        remaining = set(parameters) - set(resolved)
        resolved.update({
            p: kwargs.get(p, defaults[p]) if p in defaults else kwargs[p]
            for p in remaining
        }) # include resolved keywords
        return resolved
    return resolve


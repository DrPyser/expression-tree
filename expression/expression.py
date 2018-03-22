import abc
from utils import tupleclass, resolver
from operator import methodcaller, attrgetter
from typing import Callable, Any, Iterable, Generic, TypeVar, List
from functools import reduce

class Expression(abc.ABC):
    __slots__ = ()
    @abc.abstractmethod
    def evaluate(self, **context):
        pass


class BooleanExpression(Expression):
    """Expression that evaluates to a boolean, i.e. a condition"""
    def __and__(self, other):
        return And((self, other))

    def __or__(self, other):
        return Or((self, other))

    def __inverse__(self):
        return Not(self)

    def __bool__(self):
        return self.evaluate()


@tupleclass("clauses")
class And(BooleanExpression):
    def evaluate(self, **context):
        return all(map(methodcaller("evaluate", **context), self.clauses))


@tupleclass("clauses")
class Or(BooleanExpression):
    def evaluate(self, **context):
        return any(map(methodcaller("evaluate", **context), self.clauses))
    

@tupleclass("clause")
class Not(BooleanExpression):
    def evaluate(self, **context):
        return not self.clause.evaluate(**context)


@tupleclass("left", "right")
class Equal(BooleanExpression):
    def evaluate(self, **context):
        return self.left.evaluate(**context) == self.right.evaluate(**context)
    
    
@tupleclass("value")
class Boolean(BooleanExpression):
    """Represent a value that can be interpreted as a boolean"""
    def evaluate(self, **context):
        value = self.value.evaluate(**context)
        return bool(value)

@tupleclass("left", "right")
class Greater(BooleanExpression):
    def evaluate(self, **context):
        return self.left.evaluate(**context) > self.right.evaluate(**context)

    
@tupleclass("left", "right")
class GreaterEqual(BooleanExpression):
    def evaluate(self, **context):
        return self.left.evaluate(**context) >= self.right.evaluate(**context)


@tupleclass("left", "right")
class LesserEqual(BooleanExpression):
    def evaluate(self, **context):
        return self.left.evaluate(**context) <= self.right.evaluate(**context)


@tupleclass("left", "right")
class Lesser(BooleanExpression):
    def evaluate(self, **context):
        return self.left.evaluate(**context) < self.right.evaluate(**context)


@tupleclass("element", "container")
class In(BooleanExpression):
    def evaluate(self, **context):
        return self.element.evaluate(**context) in self.container.evaluate(**context)


class Comparable(Expression):
    def __gt__(self, other):
        return Greater(self, other)

    def __lt__(self, other):
        return Lesser(self, other)
    
    def __ge__(self, other):
        return GreaterEqual(self, other)

    def __le__(self, other):
        return LesserEqual(self, other)

    def __eq__(self, other):
        return Equal(self, other)

    def __ne__(self, other):
        return Not(Equal(self, other))

    def __contains__(self, item):
        return In(item, self)

    

@tupleclass("name", "subject")
class Attribute(Comparable):
    """Represents an attribute in an object/namespace"""
    def evaluate(self, **context):
        obj = context.get(self.subject)
        if obj:
            return getattr(obj, self.name)

        
@tupleclass("name", "subject")
class Field(Comparable):
    """Represents a field in a mapping-like object"""    
    def evaluate(self, **context):
        obj = context.get(self.subject)
        if obj:
            return obj[self.name]

        
@tupleclass("value")
class Value(Comparable):
    """Wraps a normal value"""
    def __bool__(self):
        return bool(self.value)

    def evaluate(self, **context):
        return self.value


@tupleclass("name")
class Reference(Comparable):
    def evaluate(self, **context):
        root, path = self.name.split(".", maxsplit=1)
        extractor = attrgetter(path)
        return extractor(context.get(root))
    

@tupleclass("parameters", "expression")
class Func(Expression):
    def evaluate(self, **context):
        expression = self.expression
        r = resolver(self.parameters)
        return lambda *args, **kwargs: expression.evaluate(**dict(context, **r(*args, **kwargs)))


# Selectable interface    


T = TypeVar("T")


class Selectable(Expression):
    def select(self, f: Func):
        return Select(self, f)

    def select_many(self, f: Func):
        return SelectMany(self, f)

    def filter(self, criterion: Func):
        return Filter(self, criterion)

    def reduce(self, f: Func):
        return Reduce(self, f)

    
@tupleclass("source")
class From(Selectable):
    """Represent a source of data"""
    source: Iterable[T]
    def evaluate(self, **context):
        return iter(self.source)

    
@tupleclass("source", "selection")
class Select(Selectable):
    """Represent an element-wise transformation on a source of data"""
    source: Selectable
    selection: Func
    def evaluate(self, **context):
        source = self.source.evaluate(**context)
        func = self.selection.evaluate(**context)
        return map(func, source)


@tupleclass("source", "criterion")
class Filter(Selectable):
    """Represent a filtering on a source of data"""
    source: Selectable
    criterion: Func
    def evaluate(self, **context):
        source = self.source.evaluate(**context)
        func = self.criterion.evaluate(**context)
        return filter(func, source)


@tupleclass("source", "expansion")
class SelectMany(Selectable):
    """Represent an expansion of the elements in a source of data"""
    source: Selectable
    expansion: Func
    def evaluate(self, **context):
        source = self.source.evaluate(**context)
        func = self.expansion.evaluate(**context)
        return (
            x
            for y in source
            for x in func(y)
        )

R = TypeVar("R")

@tupleclass("source", "reduction")
class Reduce(Selectable):
    """Represent a reduction on a source of data"""
    source: Selectable
    reduction: Callable[[R, T], R]
    def evaluate(self, **context):
        source = self.source.evaluate(**context)
        reduction = self.reduction.evaluate(**context)
        return reduce(reduction, source)
    


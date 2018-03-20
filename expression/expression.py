import abc
from utils import tupleclass
from operator import methodcaller

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
        return bool(self.value)

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



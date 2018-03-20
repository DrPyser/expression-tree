from functools import singledispatch
import expression as expr


@singledispatch
def compile_to_json(expression: expr.Expression):
    """Compile expression tree to json-serializable python datatypes"""
    pass

@compile_to_json.register(expr.Value)
def _(expression: expr.Value):
    return expression.value

@compile_to_json.register(expr.Boolean)
def _(expression: expr.Boolean):
    return expression.evaluate()

@compile_to_json.register(expr.In)
def _(expression: expr.In):
    return {
        "in": {
            "element": compile_to_json(expression.element),
            "container": compile_to_json(expression.container)
        }
    }

@compile_to_json.register(expr.And)
def _(expression: expr.And):
    return {
        "And": [
            compile_to_json(clause)
            for clause in expression.clauses
        ]
    }


@compile_to_json.register(expr.Or)
def _(expression: expr.Or):
    return {
        "Or": [
            compile_to_json(clause)
            for clause in expression.clauses
        ]
    }


@compile_to_json.register(expr.Equal)
def _(expression: expr.Equal):
    return {
        "Equal": {
            "left": compile_to_json(expression.left),
            "right": compile_to_json(expression.right)
        }
    }


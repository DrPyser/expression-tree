# expression-tree
Expression trees in python

This is an attempt to implement something similar to LINQ expressions trees in python,
in a clean, simple and pythonic way(where 'pythonic' means clean and simple,
and taking advantage of the features of the language).

The use case is to allow to define a generic, abstract representation of different kinds of
expressions, e.g. boolean expressions, that can then be independently compiled/converted
into another representation(e.g. JSON, SQL), or evaluated directly under a context.
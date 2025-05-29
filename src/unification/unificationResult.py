from abc import ABCMeta
from antlr4 import ParserRuleContext

from type.type import Type
from utils.singleton import SingletonABCMeta


class UnificationResult(metaclass = ABCMeta):
    expected_type: Type
    actual_type: Type
    expression: ParserRuleContext

    def __init__(self, expected_type: Type, actual_type: Type, expression: ParserRuleContext):
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.expression = expression

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.expected_type == other.expected_type and self.actual_type == other.actual_type and self.expression == other.expression

    def __str__(self) -> str:
        return f'{type(self).__name__}{{expected_type={self.expected_type.name}, actual_type={self.actual_type.name}, expression={self.expression}}}'


class UnificationFailed(UnificationResult):

    def __init__(self, expected_type: Type, actual_type: Type, expression: ParserRuleContext):
        super().__init__(expected_type, actual_type, expression)


class UnificationFailedInfiniteType(UnificationResult):

    def __init__(self, expected_type: Type, actual_type: Type, expression: ParserRuleContext):
        super().__init__(expected_type, actual_type, expression)


class UnificationSucceded(UnificationResult, metaclass = SingletonABCMeta):

    def __init__(self, expected_type: Type = None, actual_type: Type = None, expression: ParserRuleContext = None):
        super().__init__(expected_type, actual_type, expression)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return True

    def __str__(self) -> str:
        return type(self).__name__

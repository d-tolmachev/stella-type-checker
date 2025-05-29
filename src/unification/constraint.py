from antlr4 import ParserRuleContext
from typing import Self

from type.type import Type, TypeVariable


class Constraint:
    left: Type
    right: Type
    rule_context: ParserRuleContext

    def __init__(self, left: Type, right: Type, rule_context: ParserRuleContext):
        self.left = left
        self.right = right
        self.rule_context = rule_context

    def replace(self, what: TypeVariable, to: TypeVariable) -> Self:
        return Constraint(self.left.replace(what, to), self.right.replace(what, to), self.rule_context)

    def __eq__(self, other: object) -> bool:
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.left == other.left and self.right == other.right and self.rule_context == other.rule_context

    def __str__(self) -> str:
        return f'{type(self).__name__}{{left={self.left.name}, right={self.right.name}, rule_context={self.rule_context}}}'

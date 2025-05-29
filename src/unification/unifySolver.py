from antlr4 import ParserRuleContext

from type.type import FunctionalType, ListType, RecordType, SumType, TupleType, Type, TypeVariable, VariantType
from unification.constraint import Constraint
from unification.unificationResult import UnificationFailed, UnificationFailedInfiniteType, UnificationResult, UnificationSucceded


class UnifySolver:
    _constraints: list[Constraint]

    def __init__(self):
        self._constraints = []

    def add_constraint(self, left: Type, right: Type, rule_context: ParserRuleContext) -> None:
        self._constraints.append(Constraint(left, right, rule_context))

    def solve(self) -> UnificationResult:
        return UnifySolver._solve(self._constraints)

    @classmethod
    def _solve(cls, constraints: list[Constraint]) -> UnificationResult:
        if not constraints:
            return UnificationSucceded()
        constraint: Constraint = constraints[0]
        remaining_constraints: list[Constraint] = constraints[1:]
        if constraint.left == constraint.right:
            return UnifySolver._solve(remaining_constraints)
        if isinstance(constraint.left, TypeVariable) and not constraint.left.contains_in(constraint.right, constraint.rule_context):
            return UnifySolver._solve(UnifySolver._replace(remaining_constraints, constraint.left, constraint.right))
        if isinstance(constraint.right, TypeVariable) and not constraint.right.contains_in(constraint.left, constraint.rule_context):
            return UnifySolver._solve(UnifySolver._replace(remaining_constraints, constraint.right, constraint.left))
        if isinstance(constraint.left, FunctionalType) and isinstance(constraint.right, FunctionalType):
            new_constraints: list[Constraint] = [Constraint(constraint.left.param, constraint.right.param, constraint.rule_context), Constraint(constraint.left.ret, constraint.right.ret, constraint.rule_context)]
            return UnifySolver._solve(remaining_constraints + new_constraints)
        if isinstance(constraint.left, TupleType) and isinstance(constraint.right, TupleType):
            if constraint.left.arity != constraint.right.arity:
                return UnificationFailed(constraint.left, constraint.right, constraint.rule_context)
            new_constraints: list[Constraints] = []
            for left_type, right_type in zip(constraint.left.types, constraint.right.types):
                new_constraints.append(Constraint(left_type, right_type, constraint.rule_context))
            return UnifySolver._solve(remaining_constraints + new_constraints)
        if isinstance(constraint.left, RecordType) and isinstance(constraint.right, RecordType):
            left_labels: set[str] = set(constraint.left.labels)
            right_labels_indices: dict[str, int] = {label: index for index, label in enumerate(constraint.right.labels)}
            if left_labels != right_labels_indices.keys():
                return UnificationFailed(constraint.left, constraint.right, constraint.rule_context)
            new_constraints: list[Constraint] = []
            for label, left_type in zip(constraint.left.labels, constraint.left.types):
                right_type: Type = constraint.right.types[right_labels_indices[label]]
                new_constraints.append(Constraint(left_type, right_type, constraint.rule_context))
            return UnifySolver._solve(remaining_constraints + new_constraints)
        if isinstance(constraint.left, SumType) and isinstance(constraint.right, SumType):
            new_constraints: list[Constraint] = [Constraint(constraint.left.left, constraint.right.left, constraint.rule_context), Constraint(constraint.left.right, constraint.right.right, constraint.rule_context)]
            return UnifySolver._solve(remaining_constraints + new_constraints)
        if isinstance(constraint.left, VariantType) and isinstance(constraint.right, VariantType):
            left_labels: set[str] = set(constraint.left.labels)
            right_labels_indices: dict[str, int] = {label: index for index, label in enumerate(constraint.right.labels)}
            if left_labels != right_labels_indices.keys():
                return UnificationFailed(constraint.left, constraint.right, constraint.rule_context)
            new_constraints: list[Constraint] = []
            for label, left_type in zip(constraint.left.labels, constraint.left.types):
                right_type: Type = constraint.right.types[right_labels_indices[label]]
                new_constraints.append(Constraint(left_type, right_type, constraint.rule_context))
            return UnifySolver._solve(remaining_constraints + new_constraints)
        if isinstance(constraint.left, ListType) and isinstance(constraint.right, ListType):
            new_constraints: list[Constraint] = [Constraint(constraint.left.type, constraint.right.type, constraint.rule_context)]
            return UnifySolver._solve(remaining_constraints + new_constraints)
        return UnificationFailed(constraint.left, constraint.right, constraint.rule_context)

    @classmethod
    def _replace(cls, constraints: list[Constraint], what: TypeVariable, to: Type) -> list[Constraint]:
        return [constraint.replace(what, to) for constraint in constraints]

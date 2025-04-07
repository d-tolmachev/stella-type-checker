from antlr.stellaParser import stellaParser
from error.errorKind import ErrorKind
from error.errorManager import ErrorManager
from type.type import BoolType, BottomType, FunctionalType, ListType, NatType, RecordType, RefType, SumType, TopType, TupleType, Type, UnitType, VariantType
from type.typeVisitor import get_type


class ExhaustivenessValidator:
    _error_manager: ErrorManager

    def __init__(self, error_manager: ErrorManager):
        self._error_manager = error_manager

    def is_pattern_type_valid(self, ctx: stellaParser.PatternContext, expected_type: Type) -> bool:
        match ctx:
            case stellaParser.PatternFalseContext():
                actual_type: type = BoolType
            case stellaParser.PatternTrueContext():
                actual_type: type = BoolType
            case stellaParser.PatternIntContext():
                actual_type: type = NatType
            case stellaParser.PatternSuccContext():
                actual_type: type = NatType
            case stellaParser.PatternVarContext():
                return True
            case stellaParser.PatternUnitContext():
                actual_type: type = UnitType
            case stellaParser.PatternAscContext():
                ascripted_type: Type = get_type(pattern.type_)
                if ascripted_type != expected_type:
                    return False
                return self.is_pattern_type_valid(ctx.pattern_, ascripted_type)
            case stellaParser.PatternTupleContext():
                actual_type: type = TupleType
            case stellaParser.PatternRecordContext():
                actual_type: type = RecordType
            case stellaParser.PatternInlContext():
                actual_type: type = SumType
            case stellaParser.PatternInrContext():
                actual_type: type = SumType
            case stellaParser.PatternVariantContext():
                actual_type: type = VariantType
            case stellaParser.PatternListContext():
                actual_type: type = ListType
            case stellaParser.PatternConsContext():
                actual_type: type = ListType
            case stellaParser.PatternRefContext():
                actual_type: type = RefType
            case stellaParser.PatternTopContext():
                actual_type: type = TopType
            case stellaParser.PatternBottomContext():
                actual_type: type = BottomType
            case stellaParser.ParenthesisedPatternContext():
                return self.is_pattern_type_valid(pattern.pattern_, expected_type)
            case _:
                raise ValueError(f'Unsupported pattern: {type(pattern).__name__}')
        return self._validate_pattern_types(actual_type, expected_type, ctx)

    def are_pattern_types_valid(self, patterns: list[stellaParser.PatternContext], expected_type: Type) -> bool:
        for pattern in patterns:
            if not self.is_pattern_type_valid(pattern, expected_type):
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_PATTERN_FOR_TYPE, pattern, expected_type)
                return False
        return True

    def are_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext], expected_type: Type) -> bool:
        match expected_type:
            case BoolType():
                return self._are_bool_patterns_exhaustive(patterns)
            case NatType():
                return self._are_nat_patterns_exhaustive(patterns)
            case FunctionalType():
                return self._are_function_patterns_exhaustive(patterns)
            case UnitType():
                return self._are_unit_patterns_exhaustive(patterns)
            case TupleType():
                return self._are_tuple_patterns_exhaustive(patterns)
            case RecordType():
                return self._are_record_patterns_exhaustive(patterns)
            case SumType():
                return self._are_sum_patterns_exhaustive(patterns)
            case VariantType():
                return self._are_variant_patterns_exhaustive(patterns, expected_type)
            case ListType():
                return self._are_list_patterns_exhaustive(patterns)
            case RefType():
                return self._are_ref_patterns_exhaustive(patterns)
            case TopType():
                return self._are_top_patterns_exhaustive(patterns)
            case BottomType():
                return self._are_bottom_patterns_exhaustive(patterns)
            case _:
                raise ValueError('Unexpected type')

    def _validate_pattern_types(self, actual_type: type[Type], expected_type: Type, expression: stellaParser.PatternContext) -> bool:
        if actual_type is not  type(expected_type):
            return False
        if actual_type is TupleType and len(expression.patterns) != len(expected_type.types):
            return False
        if actual_type is RecordType and {record_pattern.label.text for record_pattern in expression.patterns} != set(expected_type.labels):
            return False
        if actual_type is VariantType and expression.label.text not in expected_type.labels:
            return False
        return True

    def _are_bool_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        has_false_pattern: bool = False
        has_true_pattern: Bool = False
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext):
                return True
            if isinstance(pattern, stellaParser.PatternFalseContext):
                has_false_pattern = True
            if isinstance(pattern, stellaParser.PatternTrueContext):
                has_true_pattern = True
        return has_false_pattern and has_true_pattern

    def _are_nat_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        has_int_pattern: bool = False
        has_succ_pattern: Bool = False
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext):
                return True
            if isinstance(pattern, stellaParser.PatternIntContext):
                has_int_pattern = True
            if isinstance(pattern, stellaParser.PatternSuccContext) and isinstance(pattern.pattern_, stellaParser.PatternVarContext):
                has_succ_pattern = True
        return has_int_pattern and has_succ_pattern

    def _are_function_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext):
                return True
        return False

    def _are_unit_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or isinstance(pattern, stellaParser.PatternUnitContext):
                return True
        return False

    def _are_tuple_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternTupleContext) and all(isinstance(tuple_pattern, stellaParser.PatternVarContext) for tuple_pattern in pattern.patterns)):
                return True
        return False

    def _are_record_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternRecordContext) and all(isinstance(record_pattern.pattern_, stellaParser.PatternVarContext) for record_pattern in pattern.patterns)):
                return True
        return False

    def _are_sum_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        has_inl_pattern: bool = False
        has_inr_pattern: Bool = False
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext):
                return True
            if isinstance(pattern, stellaParser.PatternInlContext):
                has_inl_pattern = True
            if isinstance(pattern, stellaParser.PatternInrContext):
                has_inr_pattern = True
        return has_inl_pattern and has_inr_pattern

    def _are_variant_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext], expected_type: VariantType) -> bool:
        actual_labels: set[str] = set()
        expected_labels: set[str] = set(expected_type.labels)
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext):
                return True
            if isinstance(pattern, stellaParser.PatternVariantContext):
                actual_labels.add(pattern.label.text)
        return not expected_labels - actual_labels

    def _are_list_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternListContext) and all(isinstance(list_pattern, stellaParser.PatternVarContext) for list_pattern in pattern.patterns)):
                return True
        return False

    def _are_ref_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        return True

    def _are_top_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or isinstance(pattern, stellaParser.PatternTopContext):
                return True
        return False

    def _are_bottom_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or isinstance(pattern, stellaParser.PatternBottomContext):
                return True
        return False

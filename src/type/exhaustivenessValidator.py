from antlr.stellaParser import stellaParser
from type.type import BoolType, BottomType, FunctionalType, ListType, NatType, RecordType, RefType, SumType, TopType, TupleType, Type, TypeVariable, UnitType, VariantType


def validate_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext], expected_type: Type) -> bool:
    preprocessed_patterns: list[stellaParser.PatternContext] = [__preprocess_pattern(pattern) for pattern in patterns]
    match expected_type:
        case BoolType():
            return __validate_bool_patterns_exhaustiveness(preprocessed_patterns)
        case NatType():
            return __validate_nat_patterns_exhaustiveness(preprocessed_patterns)
        case FunctionalType():
            return __validate_functional_patterns_exhaustiveness(preprocessed_patterns)
        case UnitType():
            return __validate_unit_patterns_exhaustiveness(preprocessed_patterns)
        case TupleType():
            return __validate_tuple_patterns_exhaustiveness(preprocessed_patterns)
        case RecordType():
            return __validate_record_patterns_exhaustiveness(preprocessed_patterns)
        case SumType():
            return __validate_sum_patterns_exhaustiveness(preprocessed_patterns)
        case VariantType():
            return __validate_variant_patterns_exhaustiveness(preprocessed_patterns, expected_type)
        case ListType():
            return __validate_list_patterns_exhaustiveness(preprocessed_patterns)
        case RefType():
            return __validate_ref_patterns_exhaustiveness(preprocessed_patterns)
        case TopType():
            return __validate_top_patterns_exhaustiveness(preprocessed_patterns)
        case BottomType():
            return __validate_bottom_patterns_exhaustiveness(preprocessed_patterns)
        case TypeVariable():
            return __validate_type_variable_patterns_exhaustiveness(preprocessed_patterns, expected_type)
        case _:
            return False

def __preprocess_pattern(pattern: stellaParser.PatternContext) -> stellaParser.PatternContext:
    match pattern:
        case stellaParser.PatternAscContext():
            return __preprocess_pattern(pattern.pattern_)
        case stellaParser.ParenthesisedPatternContext():
            return __preprocess_pattern(pattern.pattern_)
        case _:
            return pattern

def __validate_bool_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
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

def __validate_nat_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
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

def __validate_functional_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext):
            return True
    return False

def __validate_unit_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext) or isinstance(pattern, stellaParser.PatternUnitContext):
            return True
    return False

def __validate_tuple_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternTupleContext) and all(isinstance(tuple_pattern, stellaParser.PatternVarContext) for tuple_pattern in pattern.patterns)):
            return True
    return False

def __validate_record_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternRecordContext) and all(isinstance(record_pattern.pattern_, stellaParser.PatternVarContext) for record_pattern in pattern.patterns)):
            return True
    return False

def __validate_sum_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
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

def __validate_variant_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext], expected_type: VariantType) -> bool:
    actual_labels: set[str] = set()
    expected_labels: set[str] = set(expected_type.labels)
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext):
            return True
        if isinstance(pattern, stellaParser.PatternVariantContext):
            actual_labels.add(pattern.label.text)
    return not expected_labels - actual_labels

def __validate_list_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternListContext) and all(isinstance(list_pattern, stellaParser.PatternVarContext) for list_pattern in pattern.patterns)):
            return True
    return False

def __validate_ref_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    return True

def __validate_top_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext) or isinstance(pattern, stellaParser.PatternTopContext):
            return True
    return False

def __validate_bottom_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext]) -> bool:
    for pattern in patterns:
        if isinstance(pattern, stellaParser.PatternVarContext) or isinstance(pattern, stellaParser.PatternBottomContext):
            return True
    return False

def __validate_type_variable_patterns_exhaustiveness(patterns: list[stellaParser.PatternContext], expected_type: TypeVariable) -> bool:
    for pattern in patterns:
        match pattern:
            case stellaParser.PatternFalseContext():
                return __validate_bool_patterns_exhaustiveness(patterns)
            case stellaParser.PatternTrueContext():
                return __validate_bool_patterns_exhaustiveness(patterns)
            case stellaParser.PatternIntContext():
                return __validate_nat_patterns_exhaustiveness(patterns)
            case stellaParser.PatternSuccContext():
                return __validate_nat_patterns_exhaustiveness(patterns)
            case stellaParser.PatternVarContext():
                return True
            case stellaParser.PatternUnitContext():
                return __validate_unit_patterns_exhaustiveness(patterns)
            case stellaParser.PatternTupleContext():
                return __validate_tuple_patterns_exhaustiveness(patterns)
            case stellaParser.PatternRecordContext():
                return __validate_record_patterns_exhaustiveness(patterns)
            case stellaParser.PatternInlContext():
                return __validate_sum_patterns_exhaustiveness(patterns)
            case stellaParser.PatternInrContext():
                return __validate_sum_patterns_exhaustiveness(patterns)
            case stellaParser.PatternVariantContext():
                return __validate_variant_patterns_exhaustiveness(patterns, expected_type)
            case stellaParser.PatternListContext():
                return __validate_list_patterns_exhaustiveness(patterns)
            case stellaParser.PatternConsContext():
                return __validate_list_patterns_exhaustiveness(patterns)
            case stellaParser.PatternRefContext():
                return __validate_ref_patterns_exhaustiveness(patterns)
            case stellaParser.PatternTopContext():
                return __validate_top_patterns_exhaustiveness(patterns)
            case stellaParser.PatternBottomContext():
                return __validate_bottom_patterns_exhaustiveness(patterns)
    return True

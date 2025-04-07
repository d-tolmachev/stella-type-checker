from enum import Enum


class ExtensionKind(Enum):
    PREDECESSOR = (1, 'predecessor')
    NATURAL_LITERALS = (2, 'natural-literals')
    NESTED_FUNCTION_DECLARATIONS = (3, 'nested-function-declarations')
    NULLARY_FUNCTIONS = (4, 'nullary-functions')
    MULTIPARAMETER_FUNCTIONS = (5, 'multiparameter-functions')
    UNIT_TYPE = (6, 'unit-type')
    UNIT_TYPES = (7, 'unit-types')
    SEQUENCING = (8, 'sequencing')
    TYPE_ASCRIPTIONS = (9, 'type-ascriptions')
    LET_BINDINGS = (10, 'let-bindings')
    LET_MANY_BINDINGS = (11, 'let-many-bindings')
    PAIRS = (12, 'pairs')
    TUPLES = (13, 'tuples')
    RECORDS = (14, 'records')
    STRUCTURAL_PATTERNS = (15, 'structural-patterns')
    PATTERN_ASCRIPTIONS = (16, 'pattern-ascriptions')
    LET_PATTERNS = (17, 'let-patterns')
    SUM_TYPES = (18, 'sum-types')
    VARIANTS = (19, 'variants')
    NULLARY_VARIANT_LABELS = (20, 'nullary-variant-labels')
    FIXPOINT_COMBINATOR = (21, 'fixpoint-combinator')
    LETREC_BINDINGS = (22, 'letrec-bindings')
    LETREC_MANY_BINDINGS = (23, 'letrec-many-bindings')
    LISTS = (24, 'lists')
    REFERENCES = (25, 'references')
    PANIC = (26, 'panic')
    EXCEPTIONS = (27, 'exceptions')
    EXCEPTION_TYPE_DECLARATION = (28, 'exception-type-declaration')
    OPEN_VARIANT_EXCEPTIONS = (29, 'open-variant-exceptions')
    STRUCTURAL_SUBTYPING = (30, 'structural-subtyping')
    TOP_TYPE = (31, 'top-type')
    BOTTOM_TYPE = (32, 'bottom-type')
    AMBIGUOUS_TYPE_AS_BOTTOM = (33, 'ambiguous-type-as-bottom')
    TYPE_CAST = (34, 'type-cast')
    TRY_CAST_AS = (35, 'try-cast-as')
    TYPE_CAST_PATTERNS = (36, 'type-cast-patterns')

    def __init__(self, num: int, str_name: str):
        self.num = num
        self.str_name = str_name

    @classmethod
    def from_str(cls, extension_kind: str):
        match extension_kind:
            case cls.PREDECESSOR.str_name:
                return cls.PREDECESSOR
            case cls.NATURAL_LITERALS.str_name:
                return cls.NATURAL_LITERALS
            case cls.NESTED_FUNCTION_DECLARATIONS.str_name:
                return cls.NESTED_FUNCTION_DECLARATIONS
            case cls.NULLARY_FUNCTIONS.str_name:
                return cls.NULLARY_FUNCTIONS
            case cls.MULTIPARAMETER_FUNCTIONS.str_name:
                return cls.MULTIPARAMETER_FUNCTIONS
            case cls.UNIT_TYPE.str_name:
                return cls.UNIT_TYPE
            case cls.UNIT_TYPES.str_name:
                return cls.UNIT_TYPES
            case cls.SEQUENCING.str_name:
                return cls.SEQUENCING
            case cls.TYPE_ASCRIPTIONS.str_name:
                return cls.TYPE_ASCRIPTIONS
            case cls.LET_BINDINGS.str_name:
                return cls.LET_BINDINGS
            case cls.LET_MANY_BINDINGS.str_name:
                return cls.LET_MANY_BINDINGS
            case cls.PAIRS.str_name:
                return cls.PAIRS
            case cls.TUPLES.str_name:
                return cls.TUPLES
            case cls.RECORDS.str_name:
                return cls.RECORDS
            case cls.STRUCTURAL_PATTERNS.str_name:
                return cls.STRUCTURAL_PATTERNS
            case cls.PATTERN_ASCRIPTIONS.str_name:
                return cls.PATTERN_ASCRIPTIONS
            case cls.LET_PATTERNS.str_name:
                return cls.LET_PATTERNS
            case cls.SUM_TYPES.str_name:
                return cls.SUM_TYPES
            case cls.VARIANTS.str_name:
                return cls.VARIANTS
            case cls.NULLARY_VARIANT_LABELS.str_name:
                return cls.NULLARY_VARIANT_LABELS
            case cls.FIXPOINT_COMBINATOR.str_name:
                return cls.FIXPOINT_COMBINATOR
            case cls.LETREC_BINDINGS.str_name:
                return cls.LETREC_BINDINGS
            case cls.LETREC_MANY_BINDINGS.str_name:
                return cls.LETREC_MANY_BINDINGS
            case cls.LISTS.str_name:
                return cls.LISTS
            case cls.REFERENCES.str_name:
                return cls.REFERENCES
            case cls.PANIC.str_name:
                return cls.PANIC
            case cls.EXCEPTIONS.str_name:
                return cls.EXCEPTIONS
            case cls.EXCEPTION_TYPE_DECLARATION.str_name:
                return cls.EXCEPTION_TYPE_DECLARATION
            case cls.OPEN_VARIANT_EXCEPTIONS.str_name:
                return cls.OPEN_VARIANT_EXCEPTIONS
            case cls.STRUCTURAL_SUBTYPING.str_name:
                return cls.STRUCTURAL_SUBTYPING
            case cls.TOP_TYPE.str_name:
                return cls.TOP_TYPE
            case cls.BOTTOM_TYPE.str_name:
                return cls.BOTTOM_TYPE
            case cls.AMBIGUOUS_TYPE_AS_BOTTOM.str_name:
                return cls.AMBIGUOUS_TYPE_AS_BOTTOM
            case cls.TYPE_CAST.str_name:
                return cls.TYPE_CAST
            case cls.TRY_CAST_AS.str_name:
                return cls.TRY_CAST_AS
            case cls.TYPE_CAST_PATTERNS.str_name:
                return cls.TYPE_CAST_PATTERNS
            case _:
                raise ValueError(f'Can\'t find extension {extension_kind}')

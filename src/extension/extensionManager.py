from extension.extensionKind import ExtensionKind


class ExtensionManager:
    _extensions: set[ExtensionKind]

    def __init__(self):
        self._extensions = set()

    def is_predecessor(self) -> bool:
        return ExtensionKind.PREDECESSOR in self._extensions

    def is_natural_literals(self) -> bool:
        return ExtensionKind.NATURAL_LITERALS in self._extensions

    def is_nested_function_declarations(self) -> bool:
        return ExtensionKind.NESTED_FUNCTION_DECLARATIONS in self._extensions

    def is_nullary_functions(self) -> bool:
        return ExtensionKind.NULLARY_FUNCTIONS in self._extensions

    def is_multiparameter_functions(self) -> bool:
        return ExtensionKind.MULTIPARAMETER_FUNCTIONS in self._extensions

    def is_unit_type(self) -> bool:
        return ExtensionKind.UNIT_TYPE in self._extensions

    def is_unit_types(self) -> bool:
        return ExtensionKind.UNIT_TYPES in self._extensions

    def is_sequencing(self) -> bool:
        return ExtensionKind.SEQUENCING in self._extensions

    def is_type_ascriptions(self) -> bool:
        return ExtensionKind.TYPE_ASCRIPTIONS in self._extensions

    def is_let_bindings(self) -> bool:
        return ExtensionKind.LET_BINDINGS in self._extensions

    def is_let_many_bindings(self) -> bool:
        return ExtensionKind.LET_MANY_BINDINGS in self._extensions

    def is_pairs(self) -> bool:
        return ExtensionKind.PAIRS in self._extensions

    def is_tuples(self) -> bool:
        return ExtensionKind.TUPLES in self._extensions

    def is_records(self) -> bool:
        return ExtensionKind.RECORDS in self._extensions

    def is_structural_patterns(self) -> bool:
        return ExtensionKind.STRUCTURAL_PATTERNS in self._extensions

    def is_pattern_ascriptions(self) -> bool:
        return ExtensionKind.PATTERN_ASCRIPTIONS in self._extensions

    def is_let_patterns(self) -> bool:
        return ExtensionKind.LET_PATTERNS in self._extensions

    def is_sum_types(self) -> bool:
        return ExtensionKind.SUM_TYPES in self._extensions

    def is_variants(self) -> bool:
        return ExtensionKind.VARIANTS in self._extensions

    def is_nullary_variant_labels(self) -> bool:
        return ExtensionKind.NULLARY_VARIANT_LABELS in self._extensions

    def is_fixpoint_combinator(self) -> bool:
        return ExtensionKind.FIXPOINT_COMBINATOR in self._extensions

    def is_letrec_bindings(self) -> bool:
        return ExtensionKind.LETREC_BINDINGS in self._extensions

    def is_letrec_many_bindings(self) -> bool:
        return ExtensionKind.LETREC_MANY_BINDINGS in self._extensions

    def is_lists(self) -> bool:
        return ExtensionKind.LISTS in self._extensions

    def is_references(self) -> bool:
        return ExtensionKind.REFERENCES in self._extensions

    def is_panic(self) -> bool:
        return ExtensionKind.PANIC in self._extensions

    def is_exceptions(self) -> bool:
        return ExtensionKind.EXCEPTIONS in self._extensions

    def is_exception_type_declaration(self) -> bool:
        return ExtensionKind.EXCEPTION_TYPE_DECLARATION in self._extensions

    def is_open_variant_exceptions(self) -> bool:
        return ExtensionKind.OPEN_VARIANT_EXCEPTIONS in self._extensions

    def is_structural_subtyping(self) -> bool:
        return ExtensionKind.STRUCTURAL_SUBTYPING in self._extensions

    def is_top_type(self) -> bool:
        return ExtensionKind.TOP_TYPE in self._extensions

    def is_bottom_type(self) -> bool:
        return ExtensionKind.BOTTOM_TYPE in self._extensions

    def is_ambiguous_type_as_bottom(self) -> bool:
        return ExtensionKind.AMBIGUOUS_TYPE_AS_BOTTOM in self._extensions

    def is_type_cast(self) -> bool:
        return ExtensionKind.TYPE_CAST in self._extensions

    def is_try_cast_as(self) -> bool:
        return ExtensionKind.TRY_CAST_AS in self._extensions

    def is_type_cast_patterns(self) -> bool:
        return ExtensionKind.TYPE_CAST_PATTERNS in self._extensions

    def register_extension(self, extension: ExtensionKind) -> None:
        self._extensions.add(extension)

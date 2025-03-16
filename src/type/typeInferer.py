import sys

from antlr4 import ParserRuleContext

from antlr.stellaParser import stellaParser
from error.errorKind import ErrorKind
from error.errorManager import ErrorManager
from type.typeContext import TypeContext
from type.typeVisitor import get_type
from type.type import BoolType, FunctionalType, ListType, NatType, RecordType, SumType, TupleType, Type, UnitType, UnknownType, VariantType


class TypeInferer:
    _error_manager: ErrorManager
    _type_context: TypeContext

    def __init__(self, error_manager: ErrorManager, parent_type_context: TypeContext = None):
        self._error_manager = error_manager
        self._type_context = TypeContext(parent_type_context)

    def visit_expression(self, ctx: stellaParser.ExprContext, expected_type: Type) -> Type:
        match ctx:
            case stellaParser.ConstFalseContext():
                actual_type: BoolType = self._visit_const_false(ctx)
            case stellaParser.ConstTrueContext():
                actual_type: BoolType = self._visit_const_true(ctx)
            case stellaParser.ConstIntContext():
                actual_type: NatType = self._visit_const_int(ctx)
            case stellaParser.IsZeroContext():
                actual_type: BoolType = self._visit_is_zero(ctx)
            case stellaParser.SuccContext():
                actual_type: NatType = self._visit_succ(ctx)
            case stellaParser.PredContext():
                actual_type: NatType = self._visit_pred(ctx)
            case stellaParser.IfContext():
                actual_type: Type = self._visit_if(ctx, expected_type)
            case stellaParser.AbstractionContext():
                actual_type: FunctionalType = self._visit_abstraction(ctx, expected_type)
            case stellaParser.VarContext():
                actual_type: Type = self._visit_var(ctx, expected_type)
            case stellaParser.ApplicationContext():
                actual_type: Type = self._visit_application(ctx, expected_type)
            case stellaParser.ConstUnitContext():
                actual_type: UnitType = self._visit_const_unit(ctx)
            case stellaParser.TypeAscContext():
                actual_type: Type = self._visit_type_asc(ctx, expected_type)
            case stellaParser.LetContext():
                actual_type: Type = self._visit_let(ctx, expected_type)
            case stellaParser.TupleContext():
                actual_type: TupleType = self._visit_tuple(ctx, expected_type)
            case stellaParser.DotTupleContext():
                actual_type: Type = self._visit_dot_tuple(ctx, expected_type)
            case stellaParser.RecordContext():
                actual_type: RecordType = self._visit_record(ctx, expected_type)
            case stellaParser.DotRecordContext():
                actual_type: Type = self._visit_dot_record(ctx, expected_type)
            case stellaParser.MatchContext():
                actual_type: Type = self._visit_match(ctx, expected_type)
            case stellaParser.InlContext():
                actual_type: Type = self._visit_inl(ctx, expected_type)
            case stellaParser.InrContext():
                actual_type: Type = self._visit_inr(ctx, expected_type)
            case stellaParser.VariantContext():
                actual_type: VariantType = self._visit_variant(ctx, expected_type)
            case stellaParser.NatRecContext():
                actual_type: Type = self._visit_nat_rec(ctx, expected_type)
            case stellaParser.FixContext():
                actual_type: Type = self._visit_fix(ctx, expected_type)
            case stellaParser.ListContext():
                actual_type: ListType = self._visit_list(ctx, expected_type)
            case stellaParser.ConsListContext():
                actual_type: ListType = self._visit_cons_list(ctx, expected_type)
            case stellaParser.IsEmptyContext():
                actual_type: BoolType = self._visit_is_empty(ctx, expected_type)
            case stellaParser.HeadContext():
                actual_type: Type = self._visit_head(ctx, expected_type)
            case stellaParser.TailContext():
                actual_type: Type = self._visit_tail(ctx, expected_type)
            case stellaParser.TerminatingSemicolonContext():
                actual_type: Type = self.visit_expression(ctx.expr_, expected_type)
            case stellaParser.ParenthesisedExprContext():
                actual_type: Type = self.visit_expression(ctx.expr_, expected_type)
            case _:
                sys.stderr.write(f'Unsupported syntax for {type(ctx).__name__}\n')
                actual_type: Type = None
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_const_false(self, ctx: stellaParser.ConstFalseContext) -> BoolType:
        return BoolType()

    def _visit_const_true(self, ctx: stellaParser.ConstTrueContext) -> BoolType:
        return BoolType()

    def _visit_const_int(self, ctx: stellaParser.ConstIntContext) -> NatType:
        return NatType()

    def _visit_is_zero(self, ctx: stellaParser.IsZeroContext) -> BoolType:
        if not isinstance(self.visit_expression(ctx.n, NatType()), NatType):
            return None
        return BoolType()

    def _visit_succ(self, ctx: stellaParser.SuccContext) -> NatType:
        if not isinstance(self.visit_expression(ctx.n, NatType()), NatType):
            return None
        return NatType()

    def _visit_pred(self, ctx: stellaParser.PredContext) -> NatType:
        if not isinstance(self.visit_expression(ctx.n, NatType()), NatType):
            return None
        return NatType()

    def _visit_if(self, ctx: stellaParser.IfContext, expected_type: Type) -> Type:
        condition_type: Type = self.visit_expression(ctx.condition, BoolType())
        if not isinstance(condition_type, BoolType):
            return None
        then_type: Type = self.visit_expression(ctx.thenExpr, expected_type)
        if expected_type and type(then_type) is not type(expected_type):
            return None
        else_type: Type = self.visit_expression(ctx.elseExpr, expected_type)
        if expected_type and type(else_type) is not type(expected_type):
            return None
        if then_type != else_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, then_type, else_type, ctx.elseExpr)
            return None
        return then_type

    def _visit_abstraction(self, ctx: stellaParser.AbstractionContext, expected_type: Type) -> FunctionalType:
        if expected_type and not isinstance(expected_type, FunctionalType):
            expression_type: Type = self.visit_expression(ctx, None)
            if not expression_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_LAMBDA, expected_type, expression_type, ctx)
            return None
        param_type: Type = get_type(ctx._paramDecl.paramType)
        if expected_type and param_type != expected_type.param:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_PARAMETER, expected_type.param, param_type, ctx._paramDecl)
            return None
        functional_type_context: TypeContext = TypeContext(self._type_context)
        functional_type_context.save_variable_type(ctx._paramDecl.name.text, param_type)
        functional_type_inferer: TypeInferer = TypeInferer(self._error_manager, functional_type_context)
        return_type: Type = functional_type_inferer.visit_expression(ctx.returnExpr, None)
        if not return_type:
            return None
        actual_type: Type = FunctionalType(param_type, return_type)
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_var(self, ctx: stellaParser.VarContext, expected_type: Type) -> Type:
        actual_type: Type | None = self._type_context.resolve_variable_type(ctx.name.text)
        if not actual_type:
            actual_type: FunctionalType | None = self._type_context.resolve_functional_type(ctx.name.text)
        if not actual_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNDEFINED_VARIABLE, ctx.name.text)
            return None
        if expected_type and actual_type != expected_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, actual_type, ctx)
            return None
        return actual_type

    def _visit_application(self, ctx: stellaParser.ApplicationContext, expected_type: Type) -> Type:
        functional_type: Type = self.visit_expression(ctx.fun, None)
        if not functional_type:
            return None
        if not isinstance(functional_type, FunctionalType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_FUNCTION, expected_type, functional_type, ctx.fun)
            return None
        if not self.visit_expression(ctx.args[0], functional_type.param):
            return None
        actual_type: Type = functional_type.ret
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_const_unit(self, ctx: stellaParser.ConstUnitContext) -> UnitType:
        return UnitType()

    def _visit_type_asc(self, ctx: stellaParser.TypeAscContext, expected_type: Type) -> Type:
        target_type: Type = get_type(ctx.type_)
        actual_type: Type = self.visit_expression(ctx.expr_, expected_type if expected_type else target_type)
        if not actual_type:
            return None
        if actual_type != target_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, target_type, actual_type, ctx.expr_)
            return None
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_let(self, ctx: stellaParser.LetContext, expected_type: Type) -> Type:
        expression_type: Type = self.visit_expression(ctx.patternBinding(0).rhs, None)
        if not expression_type:
            return None
        expression_context: stellaParser.PatternContext = ctx.patternBinding(0).pat
        while expression_context and not isinstance(expression_context, stellaParser.PatternVarContext):
            expression_context = expression_context.pattern_
        let_type_context: TypeContext = TypeContext(self._type_context)
        let_type_context.save_variable_type(expression_context.name.text, expression_type)
        let_type_inferer: TypeInferer = TypeInferer(self._error_manager, let_type_context)
        return let_type_inferer.visit_expression(ctx.body, expected_type)

    def _visit_tuple(self, ctx: stellaParser.TupleContext, expected_type: Type) -> TupleType:
        if expected_type and not isinstance(expected_type, TupleType):
            tuple_type: TupleType = self._visit_tuple(ctx, None)
            if not tuple_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TUPLE, expected_type, tuple_type, ctx)
            return None
        types: list[Type] = []
        for expr in ctx.exprs:
            expression_type: Type = self.visit_expression(expr, None)
            if not expression_type:
                return None
            types.append(expression_type)
        return TupleType(types)

    def _visit_dot_tuple(self, ctx: stellaParser.DotTupleContext, expected_type: Type) -> Type:
        tuple_type: Type = self.visit_expression(ctx.expr_, None)
        if not tuple_type:
            return None
        if not isinstance(tuple_type, TupleType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_TUPLE, tuple_type, ctx)
            return None
        if not ctx.index.text.isnumeric() or int(ctx.index.text) <= 0 or int(ctx.index.text) > tuple_type.arity:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_TUPLE_INDEX_OUT_OF_BOUNDS, ctx.index.text, tuple_type.arity)
            return None
        actual_type: Type = tuple_type.types[int(ctx.index.text) - 1]
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_record(self, ctx: stellaParser.RecordContext, expected_type: Type) -> RecordType:
        if expected_type and not isinstance(expected_type, RecordType):
            record_type: Type = self._visit_record(ctx, None)
            if not record_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_RECORD, expected_type, record_type, ctx)
            return None
        labels: list[str] = []
        types: list[Type] = []
        for binding in ctx.bindings:
            labels.append(binding.name.text)
            type: Type = self.visit_expression(binding.rhs, None)
            if not type:
                return None
            types.append(type)
        actual_type: RecordType = RecordType(labels, types)
        if expected_type:
            if not self._is_same_record_value(actual_type, expected_type, ctx):
                return None
            return expected_type
        return actual_type

    def _visit_dot_record(self, ctx: stellaParser.DotRecordContext, expected_type: Type) -> Type:
        record_type: Type = self.visit_expression(ctx.expr_, None)
        if not record_type:
            return None
        if not isinstance(record_type, RecordType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_RECORD, record_type, ctx)
            return None
        if ctx.label.text not in record_type.labels:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_FIELD_ACCESS, ctx.label.text, record_type)
            return None
        actual_type: Type = record_type.types[record_type.labels.index(ctx.label.text)]
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_match(self, ctx: stellaParser.MatchContext, expected_type: Type) -> Type:
        expression_type: Type = self.visit_expression(ctx.expr_, None)
        if not expression_type:
            return None
        if not ctx.cases:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_ILLEGAL_EMPTY_MATCHING, ctx)
            return None
        patterns: list[stellaParser.PatternContext] = []
        for case_context in ctx.cases:
            patterns.append(case_context.pattern_)
        illegal_patterns: list[stellaParser.PatternContext] = self._find_illegal_patterns(patterns, expression_type)
        if illegal_patterns:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_PATTERN_FOR_TYPE, f'{{{", ".join([pattern.getText() for pattern in illegal_patterns])}}}', expression_type)
            return None
        if not self._are_patterns_exhaustive(patterns, expression_type):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NONEXHAUSTIVE_MATCH_PATTERNS, expression_type)
            return None
        actual_type: Type = None
        for case_context in ctx.cases:
            case_type: Type = self._visit_match_case(case_context, expression_type, expected_type)
            if not case_type:
                return None
            if actual_type and actual_type != case_type:
                if self._error_manager:
                    self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, actual_type, case_type, case_context.expr_)
                return None
            actual_type = case_type
        return actual_type

    def _visit_inl(self, ctx: stellaParser.InlContext, expected_type: Type) -> SumType:
        if not expected_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_SUM_TYPE, ctx)
            return None
        if not isinstance(expected_type, SumType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_INJECTION, expected_type)
            return None
        r = self.visit_expression(ctx.expr_, expected_type.left)
        if not r:
            return None
        return expected_type

    def _visit_inr(self, ctx: stellaParser.InrContext, expected_type: Type) -> SumType:
        if not expected_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_SUM_TYPE, ctx)
            return None
        if not isinstance(expected_type, SumType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_INJECTION, expected_type)
            return None
        if not self.visit_expression(ctx.expr_, expected_type.right):
            return None
        return expected_type

    def _visit_variant(self, ctx: stellaParser.VariantContext, expected_type: Type) -> VariantType:
        if not expected_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_VARIANT_TYPE, ctx)
            return None
        if not isinstance(expected_type, VariantType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_VARIANT, expected_type)
            return None
        if ctx.label.text not in expected_type.labels:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_VARIANT_LABEL, ctx.label.text, ctx, expected_type)
            return None
        expression_type: Type = expected_type.types[expected_type.labels.index(ctx.label.text)]
        self.visit_expression(ctx.rhs, expression_type)
        return expected_type

    def _visit_nat_rec(self, ctx: stellaParser.NatRecContext, expected_type: Type) -> Type:
        self.visit_expression(ctx.n, NatType())
        initial_type: Type = self.visit_expression(ctx.initial, expected_type)
        if not initial_type:
            return None
        step_type: Type = self.visit_expression(ctx.step, None)
        if not step_type:
            return None
        if not isinstance(step_type, FunctionalType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, FunctionalType(None, None, False), step_type, ctx.step)
            return None
        if not isinstance(step_type.param, NatType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_PARAMETER, NatType(), step_type.param, ctx.step.paramDecl if isinstance(ctx.step, stellaParser.AbstractionContext) else ctx.step)
            return None
        if not isinstance(step_type.ret, FunctionalType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, FunctionalType(None, None, False), step_type.ret, ctx.step)
            return None
        if step_type.ret.param != step_type.ret.ret:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, step_type.ret.ret, step_type.ret.param, ctx.step)
            return None
        if step_type.ret.param != initial_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, initial_type, step_type.ret.param, ctx.step)
            return None
        return initial_type

    def _visit_fix(self, ctx: stellaParser.FixContext, expected_type: Type) -> Type:
        functional_type: Type = self.visit_expression(ctx.expr_, None)
        if not functional_type:
            return None
        if not isinstance(functional_type, FunctionalType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_FUNCTION, functional_type, ctx.expr_)
            return None
        if functional_type.param != functional_type.ret:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, FunctionalType(functional_type.param, functional_type.param), functional_type, ctx.expr_)
            return None
        return functional_type.ret

    def _visit_list(self, ctx: stellaParser.ListContext, expected_type: Type) -> ListType:
        if expected_type and not isinstance(expected_type, ListType):
            list_type: ListType = self._visit_list(ctx, None)
            if not list_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_LIST, expected_type, list_type, ctx)
            return None
        if not expected_type and not ctx.exprs:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_LIST, ctx)
            return None
        expression_types: list[Type] = []
        for expr in ctx.exprs:
            type: Type = self.visit_expression(expr, None)
            if not type:
                return None
            expression_types.append(type)
        list_type: ListType = expected_type
        if not list_type and expression_types:
            list_type = ListType(expression_types[0])
        if not list_type:
            return None
        for i, expression_type in enumerate(expression_types):
            if expression_type != list_type.type:
                if self._error_manager:
                    self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, list_type, expression_type, ctx.exprs[i])
                return None
        return list_type

    def _visit_cons_list(self, ctx: stellaParser.ConsListContext, expected_type: Type) -> ListType:
        if expected_type and not isinstance(expected_type, ListType):
            list_type: ListType = self._visit_cons_list(ctx, None)
            if not list_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_LIST, expected_type, list_type, ctx)
            return None
        head_type: Type = self.visit_expression(ctx.head, None)
        if not head_type:
            return None
        if isinstance(expected_type, ListType) and expected_type.type != head_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, head_type, ctx.head)
            return None
        actual_type: ListType = ListType(head_type)
        if not self.visit_expression(ctx.tail, actual_type):
            return None
        return actual_type

    def _visit_is_empty(self, ctx: stellaParser.IsEmptyContext, expected_type: Type) -> BoolType:
        if expected_type and not isinstance(expected_type, BoolType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, BoolType(), ctx)
            return None
        list_type: Type = self.visit_expression(ctx.expr(), None)
        if not list_type:
            return None
        if not isinstance(list_type, ListType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_LIST, list_type, ctx.expr())
            return None
        return BoolType()

    def _visit_head(self, ctx: stellaParser.HeadContext, expected_type: Type) -> Type:
        list_type: Type = self.visit_expression(ctx.list_, None)
        if not list_type:
            return None
        if not isinstance(list_type, ListType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_LIST, list_type, ctx.list_)
            return None
        actual_type: Type = list_type.type
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_tail(self, ctx: stellaParser.TailContext, expected_type: Type) -> ListType:
        if expected_type and not isinstance(expected_type, ListType):
            list_type: Type = self._visit_tail(ctx, None)
            if not list_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, list_type, ctx)
            return None
        actual_type: Type = self.visit_expression(ctx.list_, None)
        if not actual_type:
            return None
        if not isinstance(actual_type, ListType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_LIST, actual_type, ctx.list_)
            return None
        return self._validate_types(actual_type, expected_type, ctx)

    def _validate_types(self, actual_type: Type, expected_type: type, expression: ParserRuleContext) -> Type:
        if not expected_type:
            return actual_type
        if isinstance(actual_type, TupleType) and actual_type.arity != expected_type.arity:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TUPLE_LENGTH, expected_type.arity, actual_type.arity, expression)
            return None
        if not actual_type or actual_type != expected_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, actual_type, expression)
            return None
        return actual_type

    def _is_same_record_value(self, actual_record: RecordType, expected_record: RecordType, ctx: stellaParser.RecordContext) -> bool:
        actual_labels: set[str] = set(actual_record.labels)
        expected_labels_indices: dict[str, int] = {label: index for index, label in enumerate(expected_record.labels)}
        missing_fields: set[str] = expected_labels_indices.keys() - actual_labels
        unexpected_fields: set[str] = actual_labels - expected_labels_indices.keys()
        if missing_fields:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_MISSING_RECORD_FIELDS, f'{{{", ".join([field for field in missing_fields])}}}', expected_record)
            return False
        if unexpected_fields:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_RECORD_FIELDS, f'{{{", ".join([field for field in unexpected_fields])}}}', expected_record)
            return False
        if len(actual_labels) < len(actual_record.labels):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_DUPLICATE_RECORD_FIELDS, expected_record)
            return None
        if len(expected_labels_indices) < len(expected_record.labels):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_DUPLICATE_RECORD_TYPE_FIELDS, expected_record)
            return None
        for label, actual_type in zip(actual_record.labels, actual_record.types):
            expected_type: Type = expected_record.types[expected_labels_indices[label]]
            both_records: bool = isinstance(actual_type, RecordType) and isinstance(expected_type, RecordType)
            if (not both_records and actual_type != expected_type) or (both_records and not self._is_same_record_value(actual_type, expected_type, ctx)):
                if self._error_manager:
                    self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, actual_type, ctx)
                return False
        return True

    def _find_illegal_patterns(self, patterns: list[stellaParser.PatternContext], type: Type) -> list[stellaParser.PatternContext]:
        match type:
            case BoolType():
                return self._find_illegal_bool_patterns(patterns)
            case NatType():
                return self._find_illegal_nat_patterns(patterns)
            case FunctionalType():
                return self._find_illegal_function_patterns(patterns)
            case UnitType():
                return self._find_illegal_unit_patterns(patterns)
            case TupleType():
                return self._find_illegal_tuple_patterns(patterns, type)
            case RecordType():
                return self._find_illegal_record_patterns(patterns, type)
            case SumType():
                return self._find_illegal_sum_patterns(patterns)
            case VariantType():
                return self._find_illegal_variant_patterns(patterns, type)
            case ListType():
                return self._find_illegal_list_patterns(patterns)
            case _:
                raise ValueError('Unexpected type')

    def _are_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext], type: Type) -> bool:
        match type:
            case BoolType():
                return self._are_bool_patterns_exhaustive(patterns)
            case NatType():
                return self._are_nat_patterns_exhaustive(patterns)
            case FunctionalType():
                return self._are_function_patterns_exhaustive(patterns)
            case UnitType():
                return self._are_unit_patterns_exhaustive(patterns)
            case TupleType():
                return self._are_tuple_patterns_exhaustive(patterns, type)
            case RecordType():
                return self._are_record_patterns_exhaustive(patterns, type)
            case SumType():
                return self._are_sum_patterns_exhaustive(patterns)
            case VariantType():
                return self._are_variant_patterns_exhaustive(patterns, type)
            case ListType():
                return self._are_list_patterns_exhaustive(patterns)
            case _:
                raise ValueError('Unexpected type')

    def _visit_match_case(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        match ctx.pattern_:
            case stellaParser.PatternVarContext():
                return self._visit_var_pattern(ctx, expression_type, expected_type)
            case stellaParser.PatternTupleContext():
                return self._visit_tuple_pattern(ctx, expression_type, expected_type)
            case stellaParser.PatternRecordContext():
                return self._visit_record_pattern(ctx, expression_type, expected_type)
            case stellaParser.PatternInlContext():
                return self._visit_inl_pattern(ctx, expression_type, expected_type)
            case stellaParser.PatternInrContext():
                return self._visit_inr_pattern(ctx, expression_type, expected_type)
            case stellaParser.PatternVariantContext():
                return self._visit_variant_pattern(ctx, expression_type, expected_type)
            case stellaParser.PatternListContext():
                return self._visit_list_pattern(ctx, expression_type, expected_type)
            case _:
                return self._visit_pattern(ctx, expected_type)

    def _find_illegal_bool_patterns(self, patterns: list[stellaParser.PatternContext]) -> list[stellaParser.PatternContext]:
        illegal_bool_patterns: list[stellaParser.PatternContext] = []
        for pattern in patterns:
            if not (isinstance(pattern, stellaParser.PatternFalseContext) or isinstance(pattern, stellaParser.PatternTrueContext) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_bool_patterns.append(pattern)
        return illegal_bool_patterns

    def _find_illegal_nat_patterns(self, patterns: list[stellaParser.PatternContext]) -> list[stellaParser.PatternContext]:
        illegal_nat_patterns: list[stellaParser.PatternContext] = []
        for pattern in patterns:
            if not (isinstance(pattern, stellaParser.PatternIntContext) or isinstance(pattern, stellaParser.PatternSuccContext) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_nat_patterns.append(pattern)
        return illegal_nat_patterns

    def _find_illegal_function_patterns(self, patterns: list[stellaParser.PatternContext]) -> list[stellaParser.PatternContext]:
        illegal_function_patterns: list[stellaParser.PatternContext] = []
        for pattern in patterns:
            if not isinstance(pattern, stellaParser.PatternVarContext):
                illegal_function_patterns.append(pattern)
        return illegal_function_patterns

    def _find_illegal_unit_patterns(self, patterns: list[stellaParser.PatternContext]) -> list[stellaParser.PatternContext]:
        illegal_unit_patterns: list[stellaParser.PatternContext] = []
        for pattern in patterns:
            if not (isinstance(pattern, stellaParser.PatternUnitContext) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_unit_patterns.append(pattern)
        return illegal_unit_patterns

    def _find_illegal_tuple_patterns(self, patterns: list[stellaParser.PatternContext], type: TupleType) -> list[stellaParser.PatternContext]:
        illegal_tuple_patterns: list[stellaParser.PatternContext] = []
        for pattern in patterns:
            if not ((isinstance(pattern, stellaParser.PatternTupleContext) and len(pattern.patterns) == len(type.types)) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_tuple_patterns.append(pattern)
        return illegal_tuple_patterns

    def _find_illegal_record_patterns(self, patterns: list[stellaParser.PatternContext], type: RecordType) -> list[stellaParser.PatternContext]:
        illegal_record_patterns: list[stellaParser.PatternContext] = []
        record_labels: set[str] = set(type.labels)
        for pattern in patterns:
            if not ((isinstance(pattern, stellaParser.PatternRecordContext) and pattern._labelledPattern.label.text in record_labels) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_record_patterns.append(pattern)
        return illegal_record_patterns

    def _find_illegal_sum_patterns(self, patterns: list[stellaParser.PatternContext]) -> list[stellaParser.PatternContext]:
        illegal_sum_patterns: list[stellaParser.PatternContext] = []
        for pattern in patterns:
            if not (isinstance(pattern, stellaParser.PatternInlContext) or isinstance(pattern, stellaParser.PatternInrContext) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_sum_patterns.append(pattern)
        return illegal_sum_patterns

    def _find_illegal_variant_patterns(self, patterns: list[stellaParser.PatternContext], type: VariantType) -> list[stellaParser.PatternContext]:
        illegal_variant_patterns: list[stellaParser.PatternContext] = []
        variant_labels: set[str] = set(type.labels)
        for pattern in patterns:
            if not ((isinstance(pattern, stellaParser.PatternVariantContext) and pattern.label.text in variant_labels) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_variant_patterns.append(pattern)
        return illegal_variant_patterns

    def _find_illegal_list_patterns(self, patterns: list[stellaParser.PatternContext]) -> list[stellaParser.PatternContext]:
        illegal_list_patterns: list[stellaParser.PatternContext] = []
        for pattern in patterns:
            if not (isinstance(pattern, stellaParser.PatternListContext) or isinstance(pattern, stellaParser.PatternConsContext) or isinstance(pattern, stellaParser.PatternVarContext)):
                illegal_list_patterns.append(pattern)
        return illegal_list_patterns

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

    def _are_tuple_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext], type: TupleType) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternTupleContext) and all(isinstance(tuple_pattern, stellaParser.PatternVarContext) for tuple_pattern in pattern.patterns)):
                return True
        return False

    def _are_record_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext], type: RecordType) -> bool:
        type_labels: set[str] = set(type.labels)
        record_labels: set[str] = set()
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext):
                return True
            if isinstance(pattern, stellaParser.PatternRecordContext):
                record_labels |= {labelled_pattern.label.text for labelled_pattern in pattern.patterns if isinstance(labelled_pattern.pattern_, stellaParser.PatternVarContext)}
        return not type_labels - record_labels

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

    def _are_variant_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext], type: VariantType) -> bool:
        type_labels: set[str] = set(type.labels)
        variant_labels: set[str] = set()
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext):
                return True
            if isinstance(pattern, stellaParser.PatternVariantContext):
                variant_labels.add(pattern.label.text)
        return not type_labels - variant_labels

    def _are_list_patterns_exhaustive(self, patterns: list[stellaParser.PatternContext]) -> bool:
        for pattern in patterns:
            if isinstance(pattern, stellaParser.PatternVarContext) or (isinstance(pattern, stellaParser.PatternListContext) and all(isinstance(list_pattern, stellaParser.PatternVarContext) for list_pattern in pattern.patterns)):
                return True
        return False

    def _visit_pattern(self, ctx: stellaParser.MatchCaseContext, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_var_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        case_type_context.save_variable_type(ctx.pattern_.name.text, expression_type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_tuple_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        for i, tuple_pattern in enumerate(ctx.pattern_.patterns):
            if isinstance(tuple_pattern, stellaParser.PatternVarContext):
                case_type_context.save_variable_type(tuple_pattern.name.text, expression_type.types[i])
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_record_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        if ctx.pattern_._labelledPattern.label.text not in expression_type.labels:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_FIELD_ACCESS, ctx.pattern_._labelledPattern.label.text, ctx.pattern_)
            return None
        for labelled_pattern in ctx.pattern_.patterns:
            if isinstance(labelled_pattern, stellaParser.PatternVarContext):
                label_type: Type = expression_type.types[expression_type.labels.index(labelled_pattern.label.text)]
                case_type_context.save_variable_type(labelled_pattern.label.text, label_type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_inl_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        if isinstance(ctx.pattern_.pattern_, stellaParser.PatternVarContext):
            case_type_context.save_variable_type(ctx.pattern_.pattern_.name.text, expression_type.left)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_inr_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        if isinstance(ctx.pattern_.pattern_, stellaParser.PatternVarContext):
            case_type_context.save_variable_type(ctx.pattern_.pattern_.name.text, expression_type.right)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_variant_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        if ctx.pattern_.label.text not in expression_type.labels:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_VARIANT_LABEL, ctx.pattern_.label.text, ctx.pattern_, expected_type)
            return None
        if isinstance(ctx.pattern_.pattern_, stellaParser.PatternVarContext):
            label_type: Type = expression_type.types[expression_type.labels.index(ctx.pattern_.label.text)]
            case_type_context.save_variable_type(ctx.pattern_.label.text, label_type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_list_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, case_type_context)
        for list_pattern in ctx.pattern_.patterns:
            if isinstance(list_pattern, stellaParser.PatternVarContext):
                case_type_context.save_variable_type(list_pattern.name.text, expression_type.type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

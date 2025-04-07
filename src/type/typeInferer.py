import sys

from antlr4 import ParserRuleContext

from antlr.stellaParser import stellaParser
from error.errorKind import ErrorKind
from error.errorManager import ErrorManager
from extension.extensionKind import ExtensionKind
from extension.extensionManager import ExtensionManager
from type.exhaustivenessValidator import ExhaustivenessValidator
from type.type import BoolType, BottomType, FunctionalType, ListType, NatType, RecordType, RefType, SumType, TopType, TupleType, Type, UnitType, UnknownType, VariantType
from type.typeContext import TypeContext
from type.typeVisitor import get_type


class TypeInferer:
    _error_manager: ErrorManager
    _extension_manager: ExtensionManager
    _type_context: TypeContext

    def __init__(self, error_manager: ErrorManager, extension_manager: ExtensionManager, parent_type_context: TypeContext = None):
        self._error_manager = error_manager
        self._extension_manager = extension_manager
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
            case stellaParser.SequenceContext():
                actual_type: Type = self._visit_sequence(ctx, expected_type)
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
                actual_type: ListType = self._visit_tail(ctx, expected_type)
            case stellaParser.RefContext():
                actual_type: RefType = self._visit_ref(ctx, expected_type)
            case stellaParser.ConstMemoryContext():
                actual_type: Type = self._visit_const_memory(ctx, expected_type)
            case stellaParser.DerefContext():
                actual_type: Type = self._visit_deref(ctx, expected_type)
            case stellaParser.AssignContext():
                actual_type: UnitType = self._visit_assign(ctx, expected_type)
            case stellaParser.PanicContext():
                actual_type: Type = self._visit_panic(ctx, expected_type)
            case stellaParser.ThrowContext():
                actual_type: Type = self._visit_throw(ctx, expected_type)
            case stellaParser.TryWithContext():
                actual_type: Type = self._visit_try_with(ctx, expected_type)
            case stellaParser.TryCatchContext():
                actual_type: Type = self._visit_try_catch(ctx, expected_type)
            case stellaParser.TypeCastContext():
                actual_type: Type = self._visit_type_cast(ctx, expected_type)
            case stellaParser.TerminatingSemicolonContext():
                actual_type: Type = self.visit_expression(ctx.expr_, expected_type)
            case stellaParser.ParenthesisedExprContext():
                actual_type: Type = self.visit_expression(ctx.expr_, expected_type)
            case _:
                sys.stderr.write(f'Unsupported syntax for {type(ctx).__name__}\n')
                actual_type: Type = None
        if not actual_type:
            return None
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
        if not condition_type:
            return None
        then_type: Type = self.visit_expression(ctx.thenExpr, expected_type)
        if not then_type:
            return None
        else_type: Type = self.visit_expression(ctx.elseExpr, then_type)
        if not else_type:
            return None
        if then_type != else_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, then_type, else_type, ctx.elseExpr)
            return None
        return else_type

    def _visit_abstraction(self, ctx: stellaParser.AbstractionContext, expected_type: Type) -> FunctionalType:
        if expected_type and not (isinstance(expected_type, FunctionalType) or isinstance(expected_type, TopType)):
            functional_type: FunctionalType = self._visit_abstraction(ctx, None)
            if not functional_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_LAMBDA, expected_type, functional_type, ctx)
            return None
        param_type: Type = get_type(ctx._paramDecl.paramType)
        functional_type_context: TypeContext = TypeContext(self._type_context)
        functional_type_context.save_variable_type(ctx._paramDecl.name.text, param_type)
        functional_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, functional_type_context)
        return_type: Type = functional_type_inferer.visit_expression(ctx.returnExpr, expected_type.ret if isinstance(expected_type, FunctionalType) else None)
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
        if expected_type and not actual_type.is_subtype_of(expected_type, self._extension_manager.is_structural_subtyping()):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_SUBTYPE if self._extension_manager.is_structural_subtyping() else ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, actual_type, ctx)
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

    def _visit_sequence(self, ctx: stellaParser.SequenceContext, expected_type: Type) -> Type:
        if not self.visit_expression(ctx.expr1, UnitType()):
            return None
        return self.visit_expression(ctx.expr2, expected_type)

    def _visit_type_asc(self, ctx: stellaParser.TypeAscContext, expected_type: Type) -> Type:
        target_type: Type = get_type(ctx.type_)
        actual_type: Type = self.visit_expression(ctx.expr_, expected_type if expected_type else target_type)
        if not actual_type:
            return None
        if not actual_type.is_subtype_of(target_type, self._extension_manager.is_structural_subtyping()):
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
        let_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, let_type_context)
        return let_type_inferer.visit_expression(ctx.body, expected_type)

    def _visit_tuple(self, ctx: stellaParser.TupleContext, expected_type: Type) -> TupleType:
        if expected_type and not (isinstance(expected_type, TupleType) or isinstance(expected_type, TopType)):
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
        actual_type: TupleType = TupleType(types)
        return actual_type

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
        if expected_type and not (isinstance(expected_type, RecordType) or isinstance(expected_type, TopType)):
            record_type: RecordType = self._visit_record(ctx, None)
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
        patterns: list[stellaParser.PatternContext] = [case_context.pattern_ for case_context in ctx.cases]
        exhaustiveness_validator: ExhaustivenessValidator = ExhaustivenessValidator(self._error_manager)
        if not exhaustiveness_validator.are_pattern_types_valid(patterns, expression_type):
            return None
        if not exhaustiveness_validator.are_patterns_exhaustive(patterns, expression_type):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NONEXHAUSTIVE_MATCH_PATTERNS, expression_type)
            return None
        actual_type: Type = None
        for case_context in ctx.cases:
            case_type: Type = self._visit_match_case(case_context, expression_type, expected_type)
            if not case_type:
                return None
            if actual_type and case_type != actual_type:
                if self._error_manager:
                    self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, actual_type, case_type, case_context.expr_)
                return None
            actual_type = case_type
        return actual_type

    def _visit_inl(self, ctx: stellaParser.InlContext, expected_type: Type) -> SumType:
        if not expected_type:
            if self._extension_manager.is_ambiguous_type_as_bottom():
                return BottomType()
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_SUM_TYPE, ctx)
            return None
        if not isinstance(expected_type, SumType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_INJECTION, expected_type)
            return None
        if not self.visit_expression(ctx.expr_, expected_type.left):
            return None
        return expected_type

    def _visit_inr(self, ctx: stellaParser.InrContext, expected_type: Type) -> SumType:
        if not expected_type:
            if self._extension_manager.is_ambiguous_type_as_bottom():
                return BottomType()
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
            if self._extension_manager.is_ambiguous_type_as_bottom():
                return BottomType()
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
        if not isinstance(step_type.ret, FunctionalType) or step_type.ret.param != step_type.ret.ret:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, FunctionalType(None, None, False), step_type.ret, ctx.step)
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
        if not isinstance(functional_type, FunctionalType) or functional_type.param != functional_type.ret:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, FunctionalType(expected_type, expected_type), functional_type, ctx.expr_)
            return None
        return functional_type.ret

    def _visit_list(self, ctx: stellaParser.ListContext, expected_type: Type) -> ListType:
        if expected_type and not (isinstance(expected_type, ListType) or isinstance(expected_type, TopType)):
            list_type: ListType = self._visit_list(ctx, None)
            if not list_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_LIST, expected_type, list_type, ctx)
            return None
        if not expected_type and not ctx.exprs:
            if self._extension_manager.is_ambiguous_type_as_bottom():
                return ListType(BottomType())
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
        for index, expression_type in enumerate(expression_types):
            if expression_type != list_type.type:
                if self._error_manager:
                    self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, list_type, expression_type, ctx.exprs[index])
                return None
        return list_type

    def _visit_cons_list(self, ctx: stellaParser.ConsListContext, expected_type: Type) -> ListType:
        if expected_type and not (isinstance(expected_type, ListType) or isinstance(expected_type, TopType)):
            list_type: ListType = self._visit_cons_list(ctx, None)
            if not list_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_LIST, expected_type, list_type, ctx)
            return None
        head_type: Type = self.visit_expression(ctx.head, None)
        if not head_type:
            return None
        if isinstance(expected_type, ListType) and not self._validate_types(head_type, expected_type.type, ctx):
            return None
        actual_type: ListType = ListType(head_type)
        if not self.visit_expression(ctx.tail, actual_type):
            return None
        return actual_type

    def _visit_is_empty(self, ctx: stellaParser.IsEmptyContext, expected_type: Type) -> BoolType:
        if expected_type and not (isinstance(expected_type, BoolType) or isinstance(expected_type, TopType)):
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
        if expected_type and not (isinstance(expected_type, ListType) or isinstance(expected_type, TopType)):
            list_type: ListType = self._visit_tail(ctx, None)
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

    def _visit_ref(self, ctx: stellaParser.RefContext, expected_type: Type) -> RefType:
        if expected_type and not (isinstance(expected_type, RefType) or isinstance(expected_type, TopType)):
            ref_type: RefType = self._visit_ref(ctx, None)
            if not ref_type:
                return None
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_REFERENCE, expected_type, ref_type, ctx)
            return None
        expression_type: Type = self.visit_expression(ctx.expr_, expected_type.inner_type if isinstance(expected_type, RefType) else None)
        if not expression_type:
            return None
        actual_type: RefType = RefType(expression_type)
        return actual_type

    def _visit_const_memory(self, ctx: stellaParser.ConstMemoryContext, expected_type: Type) -> Type:
        if not expected_type:
            if self._extension_manager.is_ambiguous_type_as_bottom():
                return RefType(BottomType())
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_REFERENCE_TYPE, ctx)
            return None
        if not isinstance(expected_type, RefType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_MEMORY_ADDRESS, ctx, expected_type)
            return None
        return expected_type

    def _visit_deref(self, ctx: stellaParser.DerefContext, expected_type: Type) -> Type:
        ref_type: Type = self.visit_expression(ctx.expr_, None)
        if not ref_type:
            return None
        if not isinstance(ref_type, RefType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, RefType(expected_type), ref_type, ctx.expr_)
            return None
        actual_type: Type = ref_type.inner_type
        return self._validate_types(actual_type, expected_type, ctx)

    def _visit_assign(self, ctx: stellaParser.AssignContext, expected_type: Type) -> UnitType:
        if expected_type and not (isinstance(expected_type, UnitType) or isinstance(expected_type, TopType)):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, UnitType(), ctx)
            return None
        lhs_type: Type = self.visit_expression(ctx.lhs, None)
        if not lhs_type:
            return None
        if not isinstance(lhs_type, RefType):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_NOT_A_REFERENCE, lhs_type, ctx.lhs)
            return None
        rhs_type: Type = self.visit_expression(ctx.rhs, None)
        if not rhs_type:
            return None
        if lhs_type.inner_type != rhs_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, lhs_type.inner_type, rhs_type, ctx.rhs)
            return None
        return UnitType()

    def _visit_panic(self, ctx: stellaParser.PanicContext, expected_type: Type) -> Type:
        if not expected_type:
            if self._extension_manager.is_ambiguous_type_as_bottom():
                return BottomType()
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_PANIC_TYPE, ctx)
            return None
        return expected_type

    def _visit_throw(self, ctx: stellaParser.ThrowContext, expected_type: Type) -> Type:
        if not expected_type:
            if self._extension_manager.is_ambiguous_type_as_bottom():
                return BottomType()
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_AMBIGUOUS_THROW_TYPE, ctx)
            return None
        exception_type: Type = self._type_context.resolve_exception_type()
        if not exception_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_EXCEPTION_TYPE_NOT_DECLARED)
            return None
        if not self.visit_expression(ctx.expr_, exception_type):
            return None
        return expected_type

    def _visit_try_with(self, ctx: stellaParser.TryWithContext, expected_type: Type) -> Type:
        try_type: Type = self.visit_expression(ctx.tryExpr, expected_type)
        if not try_type:
            return None
        with_type: Type = self.visit_expression(ctx.fallbackExpr, try_type)
        if not with_type:
            return None
        if try_type != with_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, try_type, with_type, ctx.fallbackExpr)
            return None
        return with_type

    def _visit_try_catch(self, ctx: stellaParser.TryCatchContext, expected_type: Type) -> Type:
        exhaustiveness_validator: ExhaustivenessValidator = ExhaustivenessValidator(self._error_manager)
        exception_type: Type = self._type_context.resolve_exception_type()
        if not exhaustiveness_validator.is_pattern_type_valid(ctx.pat, exception_type):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_PATTERN_FOR_TYPE, ctx.pat, exception_type)
            return None
        try_type: Type = self.visit_expression(ctx.tryExpr, expected_type)
        if not try_type:
            return None
        catch_type: Type = self.visit_expression(ctx.fallbackExpr, try_type)
        if not catch_type:
            return None
        if try_type != catch_type:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, try_type, catch_type, ctx.fallbackExpr)
            return None
        return catch_type

    def _visit_type_cast(self, ctx: stellaParser.TypeCastContext, expected_type: Type) -> Type:
        if not self.visit_expression(ctx.expr_, None):
            return None
        actual_type: Type = get_type(ctx.type_)
        return self._validate_types(actual_type, expected_type, ctx)

    def _validate_types(self, actual_type: Type, expected_type: Type, expression: ParserRuleContext) -> Type:
        if not expected_type:
            return actual_type
        if isinstance(actual_type, TupleType) and isinstance(expected_type, TupleType) and not self._validate_tuples(actual_type, expected_type, expression):
            return None
        if isinstance(actual_type, RecordType) and isinstance(expected_type, RecordType) and not self._validate_records(actual_type, expected_type, expression):
            return None
        if isinstance(actual_type, VariantType) and isinstance(expected_type, VariantType) and not self._validate_variants(actual_type, expected_type, expression):
            return None
        if not actual_type or not actual_type.is_subtype_of(expected_type, self._extension_manager.is_structural_subtyping()):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_SUBTYPE if self._extension_manager.is_structural_subtyping() else ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, expected_type, actual_type, expression)
            return None
        return expected_type

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

    def _validate_tuples(self, actual_tuple: TupleType, expected_tuple: TupleType, expression: ParserRuleContext) -> bool:
        if actual_tuple.arity < expected_tuple.arity or (not self._extension_manager.is_structural_subtyping() and actual_tuple.arity != expected_tuple.arity):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TUPLE_LENGTH, expected_tuple.arity, actual_tuple.arity, expression)
            return False
        return True

    def _validate_records(self, actual_record: RecordType, expected_record: RecordType, expression: ParserRuleContext) -> bool:
        actual_labels: set[str] = set(actual_record.labels)
        expected_labels: set[str] = set(expected_record.labels)
        missing_fields: set[str] = expected_labels - actual_labels
        unexpected_fields: set[str] = actual_labels - expected_labels
        if missing_fields:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_MISSING_RECORD_FIELDS, f'{{{", ".join([field for field in missing_fields])}}}', expected_record)
            return False
        if unexpected_fields and not self._extension_manager.is_structural_subtyping():
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_RECORD_FIELDS, f'{{{", ".join([field for field in unexpected_fields])}}}', expected_record)
            return False
        if len(actual_labels) < len(actual_record.labels):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_DUPLICATE_RECORD_FIELDS, expected_record)
            return False
        if len(expected_labels) < len(expected_record.labels):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_DUPLICATE_RECORD_TYPE_FIELDS, expected_record)
            return False
        return True

    def _validate_variants(self, actual_variant: VariantType, expected_variant: VariantType, expression: ParserRuleContext) -> bool:
        actual_labels: set[str] = set(actual_variant.labels)
        expected_labels: set[str] = set(expected_variant.labels)
        unexpected_labels: set[str] = actual_labels - expected_labels
        if unexpected_labels:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_VARIANT_LABEL, f'<|{", ".join([label for label in unexpected_labels])}|>', expression, actual_variant)
            return False
        if len(expected_labels) < len(expected_variant.labels):
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_DUPLICATE_VARIANT_TYPE_FIELDS, expected_variant)
            return False
        return True

    def _visit_pattern(self, ctx: stellaParser.MatchCaseContext, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_var_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        case_type_context.save_variable_type(ctx.pattern_.name.text, expression_type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_tuple_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        for index, tuple_pattern in enumerate(ctx.pattern_.patterns):
            if isinstance(tuple_pattern, stellaParser.PatternVarContext):
                case_type_context.save_variable_type(tuple_pattern.name.text, expression_type.types[index])
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_record_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        if ctx.pattern_._labelledPattern.label.text not in expression_type.labels:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_FIELD_ACCESS, ctx.pattern_._labelledPattern.label.text, ctx.pattern_)
            return None
        expression_labels_indices: dict[str, int] = {label: index for index, label in enumerate(expression_type.labels)}
        for labelled_pattern in ctx.pattern_.patterns:
            if isinstance(labelled_pattern, stellaParser.PatternVarContext):
                if case_type_context.resolve_variable_type(labelled_pattern.label.text):
                    if self._error_manager:
                        self._error_manager.register_error(ErrorKind.ERROR_DUPLICATE_RECORD_PATTERN_FIELDS, expected_type)
                    return None
                label_type: Type = expression_type.types[expression_labels_indices[labelled_pattern.label.text]]
                case_type_context.save_variable_type(labelled_pattern.label.text, label_type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_inl_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        if isinstance(ctx.pattern_.pattern_, stellaParser.PatternVarContext):
            case_type_context.save_variable_type(ctx.pattern_.pattern_.name.text, expression_type.left)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_inr_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        if isinstance(ctx.pattern_.pattern_, stellaParser.PatternVarContext):
            case_type_context.save_variable_type(ctx.pattern_.pattern_.name.text, expression_type.right)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_variant_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        if ctx.pattern_.label.text not in expression_type.labels:
            if self._error_manager:
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_VARIANT_LABEL, ctx.pattern_.label.text, ctx.pattern_, expected_type)
            return None
        if isinstance(ctx.pattern_.pattern_, stellaParser.PatternVarContext):
            label_type: Type = expression_type.types[expression_type.labels.index(ctx.pattern_.label.text)]
            case_type_context.save_variable_type(ctx.pattern_.pattern_.name.text, label_type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

    def _visit_list_pattern(self, ctx: stellaParser.MatchCaseContext, expression_type: Type, expected_type: Type) -> Type:
        case_type_context: TypeContext = TypeContext(self._type_context)
        case_type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, case_type_context)
        for list_pattern in ctx.pattern_.patterns:
            if isinstance(list_pattern, stellaParser.PatternVarContext):
                case_type_context.save_variable_type(list_pattern.name.text, expression_type.type)
        return case_type_inferer.visit_expression(ctx.expr_, expected_type)

from antlr4.tree.Tree import ParseTree, RuleNode
from typing import Final

from antlr.stellaParser import stellaParser
from antlr.stellaParserVisitor import stellaParserVisitor
from error.errorKind import ErrorKind
from error.errorManager import ErrorManager
from extension.extensionManager import ExtensionManager
from type.type import FunctionalType, GenericType, Type, UniversalWrapperType
from type.typeContext import TypeContext
from type.typeInferer import TypeInferer
from type.typeVisitor import get_type
from unification.unificationResult import UnificationFailed, UnificationFailedInfiniteType, UnificationResult, UnificationSucceded
from unification.unifySolver import UnifySolver


class StructureVisitor(stellaParserVisitor):
    __main_function_name: Final[str] = 'main'
    _error_manager: ErrorManager
    _is_main_found: bool

    def __init__(self, error_manager: ErrorManager):
        self._error_manager = error_manager
        self._is_main_found = False

    def visit(self, tree: ParseTree):
        if self._is_main_found:
            return None
        return super().visit(tree)

    def visitProgram(self, ctx: stellaParser.ProgramContext):
        super().visitProgram(ctx)
        if not self._is_main_found:
            self._error_manager.register_error(ErrorKind.ERROR_MISSING_MAIN)
        return None

    def visitDeclFun(self, ctx: stellaParser.DeclFunContext) -> None:
        if ctx and self.__main_function_name == ctx.name.text:
            self._is_main_found = True
            if len(ctx.paramDecls) != 1:
                self._error_manager.register_error(ErrorKind.ERROR_INCORRECT_ARITY_OF_MAIN, len(ctx.paramDecls))
        return super().visitDeclFun(ctx)


class TopLevelDeclarationVisitor(stellaParserVisitor):
    _type_context: TypeContext

    def __init__(self, type_context: TypeContext):
        self._type_context = type_context

    def visitChildren(self, node: RuleNode):
        for i in range(node.getChildCount()):
            child: RuleNode = node.getChild(i)
            if isinstance(child, stellaParser.DeclContext):
                child.accept(self)
        return None

    def visitDeclFun(self, ctx: stellaParser.DeclFunContext) -> None:
        if not ctx.paramDecls:
            return None
        param_type: Type = get_type(ctx.paramDecls[0].paramType)
        return_type: Type = get_type(ctx.returnType)
        functional_type: FunctionalType = FunctionalType(param_type, return_type)
        self._type_context.save_functional_type(ctx.name.text, functional_type)
        return None


class TypeVisitor(stellaParserVisitor):
    _error_manager: ErrorManager
    _extension_manager: ExtensionManager
    _unify_solver: UnifySolver
    _type_context: TypeContext

    def __init__(self, error_manager: ErrorManager, extension_manager: ExtensionManager, unify_solver: UnifySolver, parent_type_context: TypeContext = None):
        self._error_manager = error_manager
        self._extension_manager = extension_manager
        self._unify_solver = unify_solver
        self._type_context = TypeContext(parent_type_context)

    def visitProgram(self, ctx: stellaParser.ProgramContext):
        top_level_declaration_visitor: TopLevelDeclarationVisitor = TopLevelDeclarationVisitor(self._type_context)
        top_level_declaration_visitor.visitProgram(ctx)
        for decl in ctx.decls:
            match decl:
                case stellaParser.DeclFunContext():
                    self.visitDeclFun(decl)
                case stellaParser.DeclFunGenericContext():
                    self.visitDeclFunGeneric(decl)
                case stellaParser.DeclExceptionTypeContext():
                    self.visitDeclExceptionType(decl)
        unification_result: UnificationResult = self._unify_solver.solve()
        match unification_result:
            case UnificationFailed():
                self._error_manager.register_error(ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION, unification_result.actual_type, unification_result.expected_type, unification_result.expression)
            case UnificationFailedInfiniteType():
                self._error_manager.register_error(ErrorKind.ERROR_OCCURS_CHECK_INFINITE_TYPE, unification_result.expression)
            case UnificationSucceded():
                pass
            case _:
                raise ValueError(f'Unexpected value: {unification_result}')
        return None

    def visitDeclFun(self, ctx: stellaParser.DeclFunContext) -> None:
        functional_type: FunctionalType | None = self._type_context.resolve_functional_type(ctx.name.text)
        if not functional_type:
            return None
        expected_return_type: Type = functional_type.ret
        functional_type_context: TypeContext = TypeContext(self._type_context)
        functional_type_context.save_variable_type(ctx._paramDecl.name.text, functional_type.param)
        top_level_declaration_visitor: TopLevelDeclarationVisitor = TopLevelDeclarationVisitor(functional_type_context)
        for child in ctx.children:
            top_level_declaration_visitor.visit(child)
        functional_type_visitor: TypeVisitor = TypeVisitor(self._error_manager, self._extension_manager, self._unify_solver, functional_type_context)
        for child in ctx.children:
            functional_type_visitor.visit(child)
        type_inferer: TypeInferer = TypeInferer(self._error_manager, self._extension_manager, self._unify_solver, functional_type_context)
        type_inferer.visit_expression(ctx.returnExpr, expected_return_type)
        return None

    def visitDeclFunGeneric(self, ctx: stellaParser.DeclFunGenericContext) -> None:
        if not ctx.paramDecls:
            return None
        generic_types: list[GenericType] = [GenericType(generic.text) for generic in ctx.generics]
        param_type: Type = get_type(ctx.paramDecls[0].paramType)
        return_type: Type = get_type(ctx.returnType)
        functional_type: FunctionalType = FunctionalType(param_type, return_type)
        forall_type: UniversalWrapperType = UniversalWrapperType(generic_types, functional_type)
        self._type_context.save_functional_type(ctx.name.text, forall_type)
        return None

    def visitDeclExceptionType(self, ctx: stellaParser.DeclExceptionTypeContext) -> None:
        self._type_context.save_exception_type(get_type(ctx.exceptionType))
        return None

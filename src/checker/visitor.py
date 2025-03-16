from antlr4.tree.Tree import ParseTree, RuleNode
from typing import Final

from antlr.stellaParser import stellaParser
from antlr.stellaParserVisitor import stellaParserVisitor
from error.errorKind import ErrorKind
from error.errorManager import ErrorManager
from type.typeContext import TypeContext
from type.typeInferer import TypeInferer
from type.type import FunctionalType, Type
from type.typeVisitor import get_type


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
        param_type: Type = get_type(ctx._paramDecl.paramType)
        return_type: Type = get_type(ctx.returnType)
        functional_type: FunctionalType = FunctionalType(param_type, return_type)
        self._type_context.save_functional_type(ctx.name.text, functional_type)
        return None


class TypeVisitor(stellaParserVisitor):
    _error_manager: ErrorManager
    _type_context: TypeContext

    def __init__(self, error_manager: ErrorManager, parent_type_context: TypeContext = None):
        self._error_manager = error_manager
        self._type_context = TypeContext(parent_type_context)

    def visitProgram(self, ctx: stellaParser.ProgramContext):
        top_level_declaration_visitor: TopLevelDeclarationVisitor = TopLevelDeclarationVisitor(self._type_context)
        top_level_declaration_visitor.visitProgram(ctx)
        return super().visitProgram(ctx)

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
        functional_type_visitor: TypeVisitor = TypeVisitor(self._error_manager, functional_type_context)
        for child in ctx.children:
            functional_type_visitor.visit(child)
        type_inferer: TypeInferer = TypeInferer(self._error_manager, functional_type_context)
        type_inferer.visit_expression(ctx.returnExpr, expected_return_type)
        return None

from abc import ABCMeta, abstractmethod

from antlr.stellaParser import stellaParser
from checker.visitor import StructureVisitor, TypeVisitor
from error.errorManager import ErrorManager
from extension.extensionKind import ExtensionKind
from extension.extensionManager import ExtensionManager


class Checker(metaclass = ABCMeta):

    @abstractmethod
    def check(self, program_context: stellaParser.ProgramContext) -> None:
        pass


class StructureChecker(Checker):
    _visitor: StructureVisitor

    def __init__(self, error_manager: ErrorManager):
        self._visitor = StructureVisitor(error_manager)

    def check(self, program_context: stellaParser.ProgramContext) -> None:
        self._visitor.visitProgram(program_context)


class TypeChecker(Checker):
    _extension_manager: ExtensionManager
    _visitor: TypeVisitor

    def __init__(self, error_manager: ErrorManager):
        self._extension_manager = ExtensionManager()
        self._visitor = TypeVisitor(error_manager, self._extension_manager)

    def check(self, program_context: stellaParser.ProgramContext) -> None:
        for extension_context in program_context.extensions:
            if isinstance(extension_context, stellaParser.AnExtensionContext):
                for extension_name in extension_context.extensionNames:
                    self._extension_manager.register_extension(ExtensionKind.from_str(extension_name.text[1:]))
        self._visitor.visitProgram(program_context)

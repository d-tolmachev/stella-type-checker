from abc import ABCMeta, abstractmethod

from antlr.stellaParser import stellaParser
from checker.visitor import StructureVisitor, TypeVisitor
from error.errorManager import ErrorManager


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
    _visitor: TypeVisitor

    def __init__(self, error_manager: ErrorManager):
        self._visitor = TypeVisitor(error_manager)

    def check(self, program_context: stellaParser.ProgramContext) -> None:
        self._visitor.visitProgram(program_context)

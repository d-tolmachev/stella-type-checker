from antlr.stellaParser import stellaParser
from checker.checker import Checker, StructureChecker, TypeChecker
from error.error import Error
from error.errorManager import ErrorManager


class CheckerManager:
    _error_manager: ErrorManager
    _checkers: list[Checker]

    def __init__(self):
        self._error_manager = ErrorManager()
        self._checkers = []
        self._checkers.append(StructureChecker(self._error_manager))
        self._checkers.append(TypeChecker(self._error_manager))

    def check(self, program_context: stellaParser.ProgramContext) -> list[Error]:
        for checker in self._checkers:
            checker.check(program_context)
        return self._error_manager.errors

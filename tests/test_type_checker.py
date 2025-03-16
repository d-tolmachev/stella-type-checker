import pytest

from antlr4 import CommonTokenStream
from antlr4.InputStream import InputStream
from pathlib import Path

from antlr.stellaLexer import stellaLexer
from antlr.stellaParser import stellaParser
from checker.checkerManager import CheckerManager
from utils.singleton import SingletonABCMeta


def pytest_generate_tests(metafunc):
    test_cases = TestCases()
    if 'error_kind' in metafunc.fixturenames and 'test_case' in metafunc.fixturenames:
        metafunc.parametrize(['error_kind', 'test_case'], [[error_kind, error_case] for error_kind, error_cases in test_cases.error.items() for error_case in error_cases])
    elif 'test_case' in metafunc.fixturenames:
        metafunc.parametrize('test_case', test_cases.ok)

def test_error(error_kind, test_case):
    input = test_case.read_text()
    lexer = stellaLexer(InputStream(input))
    stream = CommonTokenStream(lexer)
    parser = stellaParser(stream)
    context = parser.program()
    checker_manager = CheckerManager()
    errors = checker_manager.check(context)
    assert errors and errors[0].error_kind.name == error_kind

def test_ok(test_case):
    input = test_case.read_text()
    lexer = stellaLexer(InputStream(input))
    stream = CommonTokenStream(lexer)
    parser = stellaParser(stream)
    context = parser.program()
    checker_manager = CheckerManager()
    errors = checker_manager.check(context)
    assert not errors


class TestCases(metaclass = SingletonABCMeta):
    __test__ = False
    __extension = '.stella'
    __test_cases_dir = Path('tests/test_cases/')
    __error_dir = Path('error/')
    __ok_dir = Path('ok/')

    def __init__(self):
        self.error = {}
        self.ok = []
        self._collect_error_test_cases()
        self._collect_ok_test_cases()

    def _collect_error_test_cases(self):
        for error_kind in self.__test_cases_dir.joinpath(self.__error_dir).iterdir():
            if error_kind.is_dir():
                self.error[error_kind.name] = list(error_kind.glob(f'*{self.__extension}'))

    def _collect_ok_test_cases(self):
        self.ok = list(self.__test_cases_dir.joinpath(self.__ok_dir).glob(f'*{self.__extension}'))

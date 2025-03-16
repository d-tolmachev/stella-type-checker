import sys

from antlr4 import CommonTokenStream
from antlr4.InputStream import InputStream

from antlr.stellaLexer import stellaLexer
from antlr.stellaParser import stellaParser
from checker.checkerManager import CheckerManager
from error.error import Error, format_error


def main() -> None:
    input: str = sys.stdin.read()
    lexer: stellaLexer = stellaLexer(InputStream(input))
    stream: CommonTokenStream = CommonTokenStream(lexer)
    parser: stellaParser = stellaParser(stream)
    context: stellaParser.ProgramContext = parser.program()
    checker_manager: CheckerManager = CheckerManager()
    errors: list[Error] = checker_manager.check(context)
    if errors:
        sys.stderr.write(format_error(errors[0], parser))
        sys.exit(-1)
    sys.exit(0)

if __name__ == '__main__':
    main()

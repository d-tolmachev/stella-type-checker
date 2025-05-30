from antlr4 import ParserRuleContext
from dataclasses import dataclass

from antlr.stellaParser import stellaParser
from error.errorKind import ErrorKind
from type.type import Type


@dataclass
class Error:
    error_kind: ErrorKind
    args: list[object]

    @property
    def error_message(self) -> str:
        match self.error_kind:
            case ErrorKind.ERROR_MISSING_MAIN:
                return 'main function is missing'
            case ErrorKind.ERROR_UNDEFINED_VARIABLE:
                return 'variable {} is undefined'
            case ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_EXPRESSION:
                return 'expected type {} but got {} for expression {}'
            case ErrorKind.ERROR_NOT_A_FUNCTION:
                return 'expected an expression of a function type but got non-function type {} for expression {}'
            case ErrorKind.ERROR_NOT_A_TUPLE:
                return 'expected an expression of a tuple type but got non-tuple type {} for expression {}'
            case ErrorKind.ERROR_NOT_A_RECORD:
                return 'expected an expression of a record type but got non-record type {} for expression {}'
            case ErrorKind.ERROR_NOT_A_LIST:
                return 'expected an expression of a list type but got non-list type {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_LAMBDA:
                return 'expected an expression of a non-function type {} but got function type {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_TYPE_FOR_PARAMETER:
                return 'expected an expression of {} type but got expression of type {} for parameter {}'
            case ErrorKind.ERROR_UNEXPECTED_TUPLE:
                return 'expected an expression of a non-tuple type {} but got tuple type {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_RECORD:
                return 'expected an expression of a non-record type {} but got record type {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_VARIANT:
                return 'expected an expression of a non-variant type {} but got variant type {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_LIST:
                return 'expected an expression of a non-list type {} but got list type {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_INJECTION:
                return 'expected sum-type but got {}'
            case ErrorKind.ERROR_MISSING_RECORD_FIELDS:
                return 'missing fields {} in record {}'
            case ErrorKind.ERROR_UNEXPECTED_RECORD_FIELDS:
                return 'unexpected fields {} in record {}'
            case ErrorKind.ERROR_UNEXPECTED_FIELD_ACCESS:
                return 'unexpected field access {} in record {}'
            case ErrorKind.ERROR_UNEXPECTED_VARIANT_LABEL:
                return 'unexpected variant labels {} in {} of type {}'
            case ErrorKind.ERROR_TUPLE_INDEX_OUT_OF_BOUNDS:
                return 'tuple index {} is out of bounds {}'
            case ErrorKind.ERROR_UNEXPECTED_TUPLE_LENGTH:
                return 'expected {} components for a tuple but got {} in tuple {}'
            case ErrorKind.ERROR_AMBIGUOUS_SUM_TYPE:
                return 'can\'t infer injection {} type'
            case ErrorKind.ERROR_AMBIGUOUS_VARIANT_TYPE:
                return 'can\'t infer the variant {} type'
            case ErrorKind.ERROR_AMBIGUOUS_LIST:
                return 'can\'t infer the list {} type'
            case ErrorKind.ERROR_ILLEGAL_EMPTY_MATCHING:
                return 'empty alternatives list for {}'
            case ErrorKind.ERROR_NONEXHAUSTIVE_MATCH_PATTERNS:
                return 'non-exhaustive patterns for type {}'
            case ErrorKind.ERROR_UNEXPECTED_PATTERN_FOR_TYPE:
                return 'unexpected pattern {} for type {}'
            case ErrorKind.ERROR_DUPLICATE_RECORD_FIELDS:
                return 'duplicate fields in record {}'
            case ErrorKind.ERROR_DUPLICATE_RECORD_TYPE_FIELDS:
                return 'duplicate fields in record of {} type'
            case ErrorKind.ERROR_DUPLICATE_VARIANT_TYPE_FIELDS:
                return 'duplicate type of field {} in variant {}'
            case ErrorKind.ERROR_INCORRECT_ARITY_OF_MAIN:
                return 'the main function must have one parameter but got {}'
            case ErrorKind.ERROR_DUPLICATE_RECORD_PATTERN_FIELDS:
                return 'duplicate fields in record pattern {}'
            case ErrorKind.ERROR_EXCEPTION_TYPE_NOT_DECLARED:
                return 'exception type is not declared'
            case ErrorKind.ERROR_AMBIGUOUS_THROW_TYPE:
                return 'can\'t infer the throw {} type'
            case ErrorKind.ERROR_AMBIGUOUS_REFERENCE_TYPE:
                return 'can\'t infer the reference {} type'
            case ErrorKind.ERROR_AMBIGUOUS_PANIC_TYPE:
                return 'can\'t infer the panic {} type'
            case ErrorKind.ERROR_NOT_A_REFERENCE:
                return 'expected an expression of a reference type but got non-reference type {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_MEMORY_ADDRESS:
                return 'unexpected memory address {} while {} is expected'
            case ErrorKind.ERROR_UNEXPECTED_SUBTYPE:
                return 'expected a subtype of {} but got  type of {} for expression {}'
            case ErrorKind.ERROR_UNEXPECTED_REFERENCE:
                return 'expected an expression of a non-reference type {} but got reference type {} for expression {}'
            case ErrorKind.ERROR_OCCURS_CHECK_INFINITE_TYPE:
                return 'infinite type found while checking expression {}'
            case ErrorKind.ERROR_NOT_A_GENERIC_FUNCTION:
                return 'expected an expression of a generic function type but got non-generic function type {} for expression {}'
            case ErrorKind.ERROR_INCORRECT_NUMBER_OF_TYPE_ARGUMENTS:
                return 'got unexpected arguments count, expected {} but got {}'
            case ErrorKind.ERROR_UNDEFINED_TYPE_VARIABLE:
                return 'type variable {} is undefined'
            case ErrorKind.ERROR_AMBIGUOUS_PATTERN_TYPE:
                return 'cam\'t infer the pattern {} type'
            case _:
                return 'unknown error'

    def _format(self, parser: stellaParser) -> str:
        formatted: list[str] = []
        formatted.append(f'ERROR: {self.error_kind.name}')
        args: list[str] = []
        for arg in self.args:
            match arg:
                case ParserRuleContext():
                    args.append(parser.getTokenStream().getText(arg.start, arg.stop))
                case Type():
                    args.append(arg.name)
                case _:
                    args.append(str(arg))
        formatted.append(self.error_message.format(*args))
        return '\n'.join(formatted)


def format_error(error: Error, parser: stellaParser) -> str:
    return f'An error occurred during type checking!\n{error._format(parser)}'

def format_errors(errors: list[Error], parser: stellaParser) -> str:
    return f'Errors occurred during type checking!{"".join([f"\n{error._format(parser)}" for error in errors])}'

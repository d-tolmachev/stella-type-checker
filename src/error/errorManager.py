from error.error import Error
from error.errorKind import ErrorKind


class ErrorManager:
    errors: list[Error]

    def __init__(self):
        self.errors = []

    def register_error(self, error_kind: ErrorKind, *args: list[object]) -> None:
        self.errors.append(Error(error_kind, args))

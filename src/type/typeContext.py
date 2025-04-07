from typing import Self

from type.type import Type, FunctionalType


class TypeContext:
    _parent: Self
    _variable_types: dict[str, Type]
    _functional_types: dict[str, FunctionalType]
    exception_type: Type

    def __init__(self, parent: Self = None):
        self._parent = parent
        self._variable_types = {}
        self._functional_types = {}
        self.exception_type = None

    def save_variable_type(self, name: str, type: Type) -> None:
        if name in self._variable_types:
            raise ValueError(f'Already known variable {name} with type {self._variable_types[name].name}')
        self._variable_types[name] = type

    def resolve_variable_type(self, name: str) -> Type | None:
        type: Type | None = self._variable_types.get(name)
        if not type and self._parent:
            return self._parent.resolve_variable_type(name)
        return type

    def save_functional_type(self, name: str, type: FunctionalType) -> None:
        if name in self._functional_types:
            raise ValueError(f'Already known function {name} with type {self._functional_types[name].name}')
        self._functional_types[name] = type

    def resolve_functional_type(self, name: str) -> FunctionalType | None:
        type: FunctionalType | None = self._functional_types.get(name)
        if not type and self._parent:
            return self._parent.resolve_functional_type(name)
        return type

    def save_exception_type(self, exception_type: Type) -> None:
        self.exception_type = exception_type

    def resolve_exception_type(self) -> Type | None:
        if not self.exception_type and self._parent:
            return self._parent.resolve_exception_type()
        return self.exception_type

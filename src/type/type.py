from abc import ABCMeta, abstractmethod

from utils.singleton import SingletonABCMeta


class Type(metaclass = ABCMeta):
    is_known_type: bool

    def __init__(self, is_known_type: bool):
        self.is_known_type = is_known_type

    @property
    @abstractmethod
    def name(self) -> str:
        pass


class UnknownType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(false)

    @property
    def name(self) -> str:
        return 'Unknown'

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UnknownType)


class BoolType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(True)

    @property
    def name(self) -> str:
        return 'Bool'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        return isinstance(other, BoolType)


class NatType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(True)

    @property
    def name(self) -> str:
        return 'Nat'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        return isinstance(other, NatType)


class FunctionalType(Type):
    param: Type
    ret: Type

    def __init__(self, param: Type, ret: Type, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.param = param
        self.ret = ret

    @property
    def name(self) -> str:
        return f'({self.param.name}) -> ({self.ret.name})' if self.is_known_type else 'UnknownFunctional'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.param == other.param and self.ret == other.ret


class UnitType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(True)

    @property
    def name(self) -> str:
        return 'Unit'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        return isinstance(other, UnitType)


class TupleType(Type):
    types: list[Type]

    def __init__(self, types: list[Type], is_known_type: bool = True):
        super().__init__(is_known_type)
        self.types = types

    @property
    def arity(self) -> int:
        return len(self.types)

    @property
    def name(self) -> str:
        return f'{{{", ".join([type.name for type in self.types])}}}' if self.is_known_type else 'UnknownTuple'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.types == other.types


class RecordType(Type):
    labels: list[str]
    types: list[Type]

    def __init__(self, labels: list[str], types: list[Type], is_known_type: bool = True):
        super().__init__(is_known_type)
        if len(labels) != len(types):
            raise ValueError('Labels and types must have same size')
        self.labels = labels
        self.types = types

    @property
    def name(self) -> str:
        return f'{{{", ".join([f"{label} : {type.name}" for label, type in zip(self.labels, self.types)])}}}' if self.is_known_type else 'UnknownRecord'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.labels == other.labels and self.types == other.types


class SumType(Type):
    left: Type
    right: Type

    def __init__(self, left: Type, right: Type, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.left = left
        self.right = right

    @property
    def name(self) -> str:
        return f'({self.left.name} + {self.right.name})' if self.is_known_type else 'UnknownSum'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.left == other.left and self.right == other.right


class VariantType(Type):
    labels: list[str]
    types: list[Type]

    def __init__(self, labels: list[str], types: list[Type], is_known_type: bool = True):
        super().__init__(is_known_type)
        if len(labels) != len(types):
            raise ValueError('Labels and types must have same size')
        self.labels = labels
        self.types = types

    @property
    def name(self) -> str:
        return f'<|{", ".join([f"{label} : {type.name}" for label, type in zip(self.labels, self.types)])}|>' if self.is_known_type else 'UnknownList'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.labels == other.labels and self.types == other.types


class ListType(Type):
    type: Type

    def __init__(self, type: Type, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.type = type

    @property
    def name(self) -> str:
        return f'List[{self.type.name}]' if self.is_known_type else 'UnknownList'

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.type == other.type

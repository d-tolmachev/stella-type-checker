from abc import ABCMeta, abstractmethod
from typing import Self

from utils.singleton import SingletonABCMeta


class Type(metaclass = ABCMeta):
    is_known_type: bool

    def __init__(self, is_known_type: bool):
        self.is_known_type = is_known_type

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def is_subtype_of(self, other: Self, subtyping_enabled: bool) -> bool:
        pass


class UnknownType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(false)

    @property
    def name(self) -> str:
        return 'Unknown'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        return other and isinstance(other, TopType)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, UnknownType)


class BoolType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(True)

    @property
    def name(self) -> str:
        return 'Bool'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        return other and isinstance(other, TopType)

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

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        return other and isinstance(other, TopType)

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

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        if other is None or type(self) is not type(other):
            return False
        return other.param.is_subtype_of(self.param, subtyping_enabled) and self.ret.is_subtype_of(other.ret, subtyping_enabled)

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

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        return other and isinstance(other, TopType)

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

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        if other is None or type(self) is not type(other):
            return False
        if len(self.types) != len(other.types):
            return False
        for self_type, other_type in zip(self.types, other.types):
            if not self_type.is_subtype_of(other_type, subtyping_enabled):
                return False
        return True

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

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        if other is None or type(self) is not type(other):
            return False
        if len(self.types) < len(other.types):
            return False
        self_labels_indices: dict[str, int] = {label: index for index, label in enumerate(self.labels)}
        for label, other_type in zip(other.labels, other.types):
            self_index: int = self_labels_indices.get(label)
            if self_index is None or not self.types[self_index].is_subtype_of(other_type, subtyping_enabled):
                return False
        return True

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        if len(self.types) != len(other.types):
            return False
        self_labels_indices: dict[str, int] = {label: index for index, label in enumerate(self.labels)}
        for label, other_type in zip(other.labels, other.types):
            self_index: int = self_labels_indices.get(label)
            if self_index is None or self.types[self_index] != other_type:
                return False
        return True


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

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        return True

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

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        if other is None or type(self) is not type(other):
            return False
        if len(self.types) > len(other.types):
            return False
        other_labels_indices: dict[str, int] = {label: index for index, label in enumerate(other.labels)}
        for label, self_type in zip(self.labels, self.types):
            other_index: int = other_labels_indices.get(label)
            if other_index is None or not self_type.is_subtype_of(other.types[other_index], subtyping_enabled):
                return False
        return True

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        if len(self.types) != len(other.types):
            return False
        other_labels_indices: dict[str, int] = {label: index for index, label in enumerate(other.labels)}
        for label, self_type in zip(self.labels, self.types):
            other_index: int = other_labels_indices.get(label)
            if other_index is None or self_type != other.types[other_index]:
                return False
        return True


class ListType(Type):
    type: Type

    def __init__(self, type: Type, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.type = type

    @property
    def name(self) -> str:
        return f'List[{self.type.name}]' if self.is_known_type else 'UnknownList'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        if other is None or type(self) is not type(other):
            return False
        return self.type.is_subtype_of(other.type, subtyping_enabled)

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.type == other.type


class RefType(Type):
    inner_type: Type

    def __init__(self, inner_type: Type, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.inner_type = inner_type

    @property
    def name(self) -> str:
        return f'&{self.inner_type.name}'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        if other is None or type(self) is not type(other):
            return False
        return self.inner_type.is_subtype_of(other.inner_type, subtyping_enabled)

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.inner_type == other.inner_type


class TopType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(True)

    @property
    def name(self) -> str:
        return 'Top'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        return self is other

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        return isinstance(other, TopType)


class BottomType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(True)

    @property
    def name(self) -> str:
        return 'Bottom'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        return subtyping_enabled

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        return isinstance(other, BottomType)

from abc import ABCMeta, abstractmethod
from antlr4 import ParserRuleContext
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

    def replace(self, what: Self, to: Self) -> Self:
        return self

    def get_first_unresolved_type(self) -> Self:
        return None


class UnknownType(Type, metaclass = SingletonABCMeta):

    def __init__(self):
        super().__init__(False)

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

    def replace(self, what: Type, to: Type) -> Type:
        return FunctionalType(self.param.replace(what, to), self.ret.replace(what, to))

    def get_first_unresolved_type(self) -> Type:
        param_first_unresolved_type: Type = self.param.get_first_unresolved_type()
        if param_first_unresolved_type:
            return param_first_unresolved_type
        return self.ret.get_first_unresolved_type()

    def with_substitution(self, types: dict[Type, Type]) -> Self:
        new_param: Type = self.param
        new_ret: Type = self.ret
        for generic_type, type in types.items():
            new_param = self._substitute(new_param, generic_type, type)
            new_ret = self._substitute(new_ret, generic_type, type)
        return FunctionalType(new_param, new_ret)

    def _substitute(self, original: Type, generic: Type, replacement: Type) -> Type:
        match original:
            case FunctionalType():
                return FunctionalType(self._substitute(original.param, generic, replacement), self._substitute(original.ret, generic, replacement))
            case TupleType():
                return TupleType([self._substitute(tuple_type, generic, replacement) for tuple_type in original.types])
            case RecordType():
                return RecordType(original.labels, [self._substitute(record_type, generic, replacement) for record_type in original.types])
            case SumType():
                return SumType(self._substitute(original.left, generic, replacement), self._substitute(original.right, generic, replacement))
            case VariantType():
                return VariantType(original.labels, [self._substitute(variant_type, generic, replacement) for variant_type in original.types])
            case ListType():
                return ListType(self._substitute(original.type, generic, replacement))
            case GenericType():
                return replacement if original == generic else original
            case UniversalWrapperType():
                return UniversalWrapperType([type_param for type_param in original.type_params if type_param != generic], self._substitute(original.inner_type, generic, replacement))
            case _:
                return original

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

    def replace(self, what: Type, to: Type) -> Type:
        return TupleType([tuple_type.replace(what, to) for tuple_type in self.types])

    def get_first_unresolved_type(self) -> Type:
        for tuple_type in self.types:
            first_unresolved_type: Type = tuple_type.get_first_unresolved_type()
            if first_unresolved_type:
                return first_unresolved_type
        return None

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

    def replace(self, what: Type, to: Type) -> Type:
        return RecordType(self.labels, [record_type.replace(what, to) for record_type in self.types])

    def get_first_unresolved_type(self) -> Type:
        for record_type in self.types:
            first_unresolved_type: Type = record_type.get_first_unresolved_type()
            if first_unresolved_type:
                return first_unresolved_type
        return None

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
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        if other is None or type(self) is not type(other):
            return False
        return self.left.is_subtype_of(other.left, subtyping_enabled) and self.right.is_subtype_of(other.right, subtyping_enabled)

    def replace(self, what: Type, to: Type) -> Type:
        return SumType(self.left.replace(what, to), self.right.replace(what, to))

    def get_first_unresolved_type(self) -> Type:
        left_first_unresolved_type: Type = self.left.get_first_unresolved_type()
        if left_first_unresolved_type:
            return left_first_unresolved_type
        return self.right.get_first_unresolved_type()

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
        return f'<|{", ".join([f"{label} : {type.name}" for label, type in zip(self.labels, self.types)])}|>'

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

    def replace(self, what: Type, to: Type) -> Type:
        return VariantType(self.labels, [variant_type.replace(what, to) for variant_type in self.types])

    def get_first_unresolved_type(self) -> Type:
        for variant_type in self.types:
            first_unresolved_type: Type = variant_type.get_first_unresolved_type()
            if first_unresolved_type:
                return first_unresolved_type
        return None

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

    def replace(self, what: Type, to: Type) -> Type:
        return ListType(self.type.replace(what, to))

    def get_first_unresolved_type(self) -> Type:
        return self.type.get_first_unresolved_type()

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

    def replace(self, what: Type, to: Type) -> Type:
        return RefType(self.inner_type.replace(what, to))

    def get_first_unresolved_type(self) -> Type:
        return self.inner_type.get_first_unresolved_type()

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


class TypeVariable(Type):
    index: int
    _count: int = 0

    def __init__(self, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.index = TypeVariable._count
        TypeVariable._count += 1

    @property
    def name(self) -> str:
        return f'?T{self.index}'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        return other and isinstance(other, TopType)

    def replace(self, what: Self, to: Type) -> Type:
        return to if self == what else self

    def contains_in(self, type: Type, expression: ParserRuleContext) -> bool:
        match type:
            case FunctionalType():
                result: bool = self.contains_in(type.param, expression) or self.contains_in(type.ret, expression)
            case TupleType():
                try:
                    result: bool = any(self.contains_in(tuple_type, expression) for tuple_type in type.types)
                except Exception:
                    result: bool = False
            case RecordType():
                try:
                    result: bool = any(self.contains_in(record_type, expression) for record_type in type.types)
                except Exception:
                    result: bool = False
            case SumType():
                result: bool = self.contains_in(type.left, expression) or self.contains_in(type.right, expression)
            case VariantType():
                result: bool = any(self.contains_in(variant_type, expression) for variant_type in type.types)
            case ListType():
                result: bool = self.contains_in(type.type, expression)
            case TypeVariable():
                result: bool = self == type
            case _:
                result: bool = False
        if result:
            raise ValueError()
        return False

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.index == other.index


class GenericType(Type):
    variable_name: str

    def __init__(self, variable_name: str, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.variable_name = variable_name

    @property
    def name(self) -> str:
        return f'[{self.variable_name}]'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        return other and isinstance(other, TopType)

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.variable_name == other.variable_name

    def __hash__(self) -> int:
        return hash(self.variable_name)


class UniversalWrapperType(Type):
    type_params: GenericType
    inner_type: Type

    def __init__(self, type_params: list[GenericType], inner_type: Type, is_known_type: bool = True):
        super().__init__(is_known_type)
        self.type_params = type_params
        self.inner_type = inner_type

    @property
    def name(self) -> str:
        return f'[{", ".join([type_param.name for type_param in self.type_params])}]{self.inner_type.name}'

    def is_subtype_of(self, other: Type, subtyping_enabled: bool) -> bool:
        if self == other:
            return True
        if not subtyping_enabled:
            return False
        return other and isinstance(other, TopType)

    def __eq__(self, other: object) -> bool:
        if not self.is_known_type or (isinstance(other, Type) and not other.is_known_type):
            return True
        if self is other:
            return True
        if other is None or type(self) is not type(other):
            return False
        return self.type_params == other.type_params and self.inner_type == other.inner_type

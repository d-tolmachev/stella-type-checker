from antlr.stellaParser import stellaParser
from type.type import BoolType, FunctionalType, ListType, NatType, RecordType, SumType, TupleType, Type, UnitType, UnknownType, VariantType


def get_type(ctx: stellaParser.StellatypeContext) -> Type:
    match ctx:
        case stellaParser.TypeBoolContext():
            return __visit_bool_type(ctx)
        case stellaParser.TypeNatContext():
            return __visit_nat_type(ctx)
        case stellaParser.TypeFunContext():
            return __visit_functional_type(ctx)
        case stellaParser.TypeUnitContext():
            return __visit_unit_type(ctx)
        case stellaParser.TypeTupleContext():
            return __visit_tuple_type(ctx)
        case stellaParser.TypeRecordContext():
            return __visit_record_type(ctx)
        case stellaParser.TypeSumContext():
            return __visit_sum_type(ctx)
        case stellaParser.TypeVariantContext():
            return __visit_variant_type(ctx)
        case stellaParser.TypeListContext():
            return __visit_list_type(ctx)
        case stellaParser.TypeParensContext():
            return get_type(ctx.type_)
        case _:
            return UnknownType()

def __visit_bool_type(ctx: stellaParser.TypeBoolContext) -> BoolType:
    return BoolType()

def __visit_nat_type(ctx: stellaParser.TypeNatContext) -> NatType:
    return NatType()

def __visit_functional_type(ctx: stellaParser.TypeFunContext) -> FunctionalType:
    return FunctionalType(get_type(ctx.paramTypes[0]), get_type(ctx.returnType))

def __visit_unit_type(ctx: stellaParser.TypeUnitContext) -> UnitType:
    return UnitType()

def __visit_tuple_type(ctx: stellaParser.TypeTupleContext) -> TupleType:
    return TupleType([get_type(type) for type in ctx.types])

def __visit_record_type(ctx: stellaParser.TypeRecordContext) -> RecordType:
    labels: list[str] = []
    types: list[Type] = []
    for field in ctx.fieldTypes:
        labels.append(field.label.text)
        types.append(get_type(field.type_))
    return RecordType(labels, types)

def __visit_sum_type(ctx: stellaParser.TypeSumContext) -> SumType:
    return SumType(get_type(ctx.left), get_type(ctx.right))

def __visit_variant_type(ctx: stellaParser.TypeVariantContext) -> VariantType:
    labels: list[str] = []
    types: list[Type] = []
    for field in ctx.fieldTypes:
        labels.append(field.label.text)
        types.append(get_type(field.type_))
    return VariantType(labels, types)

def __visit_list_type(ctx: stellaParser.TypeListContext) -> ListType:
    return ListType(get_type(ctx.type_))

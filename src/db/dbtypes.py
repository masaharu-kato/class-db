"""
    sql.datatypes - The definitions of data types in the database system
"""
import types
from typing import Any, Collection, Type, Optional, Union
import datetime
import dataclasses


class ExType:
    def __init__(self,
        basetype: Type,
        *,
        val_range: Optional[Collection[int]] = None,
        len_range: Optional[Collection[int]] = None,
    ) -> None:
        self.basetype = basetype
        self.val_range = val_range
        self.len_range = len_range

    def is_valid(self, val:Any) -> bool:
        return (
            isinstance(val, self.basetype)
            and (self.val_range is None or val in self.val_range)
            and (self.len_range is None or len(val) in self.len_range)
        )

    def expect_valid(self, val:Any) -> None:
        if not self.is_valid(val):
            raise TypeError('The given value is not valid.')


class RangedType(ExType):
    def __init__(self, basetype:Type, val_range:Collection[int]):
        super().__init__(basetype, val_range=val_range)


class LenLimitedType(ExType):
    def __init__(self, basetype:Type, max_len:int):
        super().__init__(basetype, len_range=range(0, max_len + 1))


@dataclasses.dataclass
class DataTypeInfo:
    dbtype: Optional[str]
    pytype: ExType
    nullable: bool = False
    primary: bool = False
    auto_increment: bool = False
    unique: bool = False
    link_table: Optional[Type] = None

    def sql_expr(self) -> str:
        """ generate sql expr """
        sql = self.dbtype
        if not self.nullable:
            sql += ' NOT NULL'
        if self.primary:
            sql += ' PRIMARY KEY'
        if self.auto_increment:
            sql += ' AUTO_INCREMENT'
        if self.unique:
            sql += ' UNIQUE'
        return sql

class DataTypeBase:
    pass


def DataType(base:Any, **kwargs):

    if base == None:
        data_type_info = DataTypeInfo(**kwargs)
    elif isinstance(base, DataTypeInfo):
        data_type_info = DataTypeInfo(**{**dataclasses.asdict(data_type_info), **kwargs})
    elif issubclass(base, DataTypeBase):
        data_type_info = DataTypeInfo(**{**dataclasses.asdict(base.info), **kwargs})
    # elif isinstance(base, dict):
    #     data_type_info = DataTypeInfo(**{**base, **kwargs})
    else:
        raise RuntimeError('Unexpected type of `base`.')

    sql_expr = data_type_info.sql_expr()

    class DataTypeMeta(type):
        def __init__(cls, name, bases, attribute):
            super(DataTypeMeta, cls).__init__(name, bases, attribute)
            cls.info = data_type_info
            cls.sql_expr = sql_expr

    return types.new_class(sql_expr, bases=(DataTypeBase,), kwds=dict(metaclass=DataTypeMeta))


def NewDataType(
    dbtype:Optional[str],
    pytype:ExType,
    **options
):
    return DataType(None, dbtype=dbtype, pytype=pytype, **options)


def PrimaryKey(
    base_datatype,
    *,
    auto_increment:bool=False,
    **options
):
    return DataType(base_datatype, primary=True, auto_increment=auto_increment, **options)

def IDKey(*, auto_increment:bool=False, **options):
    return PrimaryKey(Int, auto_increment=auto_increment, **options)

def ForeignKey(link_table:Type):
    return DataType(Int, link_table=link_table)


# 
# 
# def sql_expr(t:Any) -> str:
#     if isinstance(t, Type):
#         metatype = getattr(t, 'metatype')
#         if metatype == 'DataType':
#             return t.dbtype
#         if metatype == 'Primary':
#             return f'{t.dbtype} PRIMARY KEY{' AUTO_INCREMENT' if t.auto_increment else ''}'
# 



def _singed_range(bits:int) -> Collection[int]:
    return range(-(2 ** (bits - 1)), 2 ** (bits - 1))

def _unsigned_range(bits:int) -> Collection[int]:
    return range(0, (2 ** bits))



TinyInt   = NewDataType('TINYINT'  , RangedType(int, _singed_range( 8)))
SmallInt  = NewDataType('SMALLINT' , RangedType(int, _singed_range(16)))
MediumInt = NewDataType('MEDIUMINT', RangedType(int, _singed_range(24)))
Int       = NewDataType('INT'      , RangedType(int, _singed_range(32)))
BigInt    = NewDataType('BIGINT'   , RangedType(int, _singed_range(64)))

UnsignedTinyInt   = NewDataType('UNSIGNED TINYINT'  , RangedType(int, _unsigned_range( 8)))
UnsignedSmallInt  = NewDataType('UNSIGNED SMALLINT' , RangedType(int, _unsigned_range(16)))
UnsignedMediumInt = NewDataType('UNSIGNED MEDIUMINT', RangedType(int, _unsigned_range(24)))
UnsignedInt       = NewDataType('UNSIGNED INT'      , RangedType(int, _unsigned_range(32)))
UnsignedBigInt    = NewDataType('UNSIGNED BIGINT'   , RangedType(int, _unsigned_range(64)))

Float   = NewDataType('FLOAT'  , ExType(float))
Double  = NewDataType('DOUBLE' , ExType(float))
Real    = NewDataType('REAL'   , ExType(float))
Decimal = NewDataType('DECIMAL', ExType(float))

def Char(l:int):
    return NewDataType(f'CHAR({l})', LenLimitedType(str, l))

def VarChar(l:int):
    return NewDataType(f'VARCHAR({l})', LenLimitedType(str, l))

def Binary(l:int):
    return NewDataType(f'BINARY({l})', LenLimitedType(bytes, l))

def VarBinary(l:int):
    return NewDataType(f'VARBINARY({l})', LenLimitedType(bytes, l))

TinyBlob   = NewDataType('TINYBLOB'  , LenLimitedType(bytes, 2 **  8 - 1))
Blob       = NewDataType('BLOB'      , LenLimitedType(bytes, 2 ** 16 - 1))
MediumBlob = NewDataType('MEDIUMBLOB', LenLimitedType(bytes, 2 ** 24 - 1))
LongBlob   = NewDataType('LONGBLOB'  , LenLimitedType(bytes, 2 ** 32 - 1))

TinyText   = NewDataType('TINYTEXT'  , LenLimitedType(str, 2 **  8 - 1))
Text       = NewDataType('TEXT'      , LenLimitedType(str, 2 ** 16 - 1))
MediumText = NewDataType('MEDIUMTEXT', LenLimitedType(str, 2 ** 24 - 1))
LongText   = NewDataType('LONGTEXT'  , LenLimitedType(str, 2 ** 32 - 1))

# class Enum:
#     pass

# class Set:
#     pass


Date = NewDataType('DATE', ExType(datetime.date))
Time = NewDataType('TIME', ExType(datetime.time))
DateTime = NewDataType('DATETIME', ExType(datetime.datetime))

# class Timestamp(datetime.datetime):
#     pass

# class Year(int):
#     pass

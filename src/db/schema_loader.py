from db import dbtypes as dbt
from db import database
from typing import Any, Dict, List, Iterator, Set, Sequence, Type, Union, Optional, get_type_hints


def set_database(db:database.Database):
    pass


class TableMetaClass(type):

    current_db:Optional[database.Database] = None

    def __new__(cls, cls_name, cls_bases, cls_dict, **options):
        
        type_hints:Dict[str, Any] = get_type_hints(table_class)
        self.table_name = type_hints['__table_name__'] if '__table_name__' in type_hints else table_class.__name__

        # generate columns and foregin keys
        self.columns:Dict[str, dbt.DataTypeBase] = {}
        _key_name:Optional[str] = None
        self.foreign_keys_table:Dict[str, TableBase] = {}
        for name, _type in type_hints.items():
            if name.startswith('__'): continue
            datatype = to_data_type(_type)
            self.columns[name] = datatype

            # If this column is primary key, save this key's name
            if datatype.info.primary:
                if _key_name is not None:
                    raise RuntimeError('Multiple primary key is not allowed.')
                _key_name = name

            # If this column is foreign key, append to list
            if datatype.info.link_table:
                self.foreign_keys_table[name] = datatype.info.link_table

        if _key_name is None:
            raise RuntimeError('Primary key not found.')

        self.key_column_name = _key_name


class TableBase:
    """ Base class of a Table in the database """

    @classmethod
    def 

    @classmethod
    def metadata(cls):
        if not hasattr(cls, '__metadata__'):
            cls.__metadata__ = TableMetadata(cls)
        return cls.__metadata__
    
    @classmethod
    def select(cls, *,
        where:str,
        order:List[Tuple[str, str]],
        count:int,
        offset:int,
        columns_to_load:Set[str],
    ) -> Iterator:
        """ Select records from the database """

    @classmethod
    def select_one(cls, key_v) -> Iterator:
        """ Select just one record using primary key from the database 
        """


    """ Instance methods """

    def load(self) -> None:
        """ Select (the latest version of) this record from the database """

    def save(self) -> None:
        """ Insert or update this record to the database """

    def insert(self) -> None:
        """ Insert this record as new record
            If the record already exists on the database, throw a exception.
        """

    def delete(self) -> None:
        """ Delete this record from the database """



class RawTable(TableBase):
    """ """


class Table(RawTable):
    """ """
    id: dbt.IDKey(auto_increment=True)

class UniqueTable(Table):
    """ """


def create_tables(*tables:List[Type]):
    for table in tables:
        # print(f'# {table.__name__}')
        # type_hints = get_type_hints(table)
        # for k, v in type_hints.items():
        #     print(f'    {k}: {v}')
        print(table.show_create_table())
        if issubclass(table, UniqueTable):
            print(table.show_selsert())
        print('')


def to_data_type(t:Any, **options):

    if isinstance(t, type):

        # if `t` is already DataType
        if issubclass(t, dbt.DataTypeBase):
            if options:
                return dbt.DataType(t, **options)
            return t

        if issubclass(t, TableBase):
            return dbt.ForeignKey(t)

    # assume typing.Optional type
    if getattr(t, '__origin__') == Union:
        if len(t.__args__) != 2:
            raise RuntimeError('This union type is not available.')
        if t.__args__[0] == type(None):
            return to_data_type(t.__args__[1], nullable=True)
        elif t.__args__[1] == type(None):
            return to_data_type(t.__args__[0], nullable=True)
        else:
            raise RuntimeError('This union type is not available.')

    raise RuntimeError('Failed to convert to data type.')
    
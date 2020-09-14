from db import dbtypes as dbt
from typing import Any, Dict, List, Iterator, Sequence, Type, Union, Optional, get_type_hints


class TableMetadata:
    def __init__(self, table_class):
        
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
    def metadata(cls):
        if not hasattr(cls, '__metadata__'):
            cls.__metadata__ = TableMetadata(cls)
        return cls.__metadata__

    @classmethod
    def show_create_table(cls) -> str:
        metadata = cls.metadata()
        table_name = metadata.table_name
        columns = metadata.columns
        fk_table = metadata.foreign_keys_table
        return (
            f'CREATE TABLE `{table_name}`(\n  ' + ', \n  '.join((
                *(f'`{name}` {dt.sql_expr}' for name, dt in columns.items()),
                *(
                    f'FOREIGN KEY `fk_{name}` (`{name}`) REFERENCES `{t.metadata().table_name}`(`{t.metadata().key_column_name}`)'
                    for name, t in fk_table.items()
                ),
            )) + '\n);'
        )
    
    @classmethod
    def select(cls, where, order, count, offset) -> Iterator:
        """ Select records from the database """

    @classmethod
    def select_one(cls, where) -> Iterator:
        """ Select just one record from the database 
            If more than one records are found, throw a exception.
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

    @classmethod
    def show_selsert(cls, arg_colnames:Optional[List[str]] = None) -> str:
        metadata = cls.metadata()
        table_name = metadata.table_name
        columns = metadata.columns
        key_name = metadata.key_column_name
        
        _v_colnames = {name for name in columns.keys() if name != key_name}
        
        if arg_colnames is not None:
            if len(arg_colnames) != len(set(arg_colnames)):
                raise RuntimeError('Duplicate argument column names.')
            if not all(colname in _v_colnames for colname in arg_colnames):
                raise RuntimeError('Unknown column(s) exist in argument column names.')
            v_colnames = arg_colnames
        else:
            v_colnames = list(_v_colnames)
            
        return (
             'DELIMITER //\n' + 
            f'CREATE FUNCTION `selsert_{table_name}`(  \n' + ', '.join(
                f'v_{name} {columns[name].info.dbtype}' for name in v_colnames
            ) + 
             ')\n' + 
            f'RETURNS {columns[key_name].info.dbtype} DETERMINISTIC\n' + 
             'BEGIN\n' +
               '@ret = (\n' + 
                 f'SELECT `{key_name}` FROM `{table_name}`\n' + 
                 f'WHERE ' + ' AND '.join(
                f'`{name}` = v_{name}' for name in v_colnames
            ) + 
             '  );\n' +
             '  IF @ret IS NOT NULL THEN\n' +
             '    RETURN @ret;\n' +
             '  END IF;\n' +
            f'  INSERT INTO `{key_name}`(' + ', '.join(f'`{name}`' for name in v_colnames) + ') \n' + 
             '    VALUES(' + ', '.join(f'v_{name}' for name in v_colnames) + ');\n' +
             '  RETURN LAST_INSERT_ID();\n' +
             'END//\n' +
             'DELIMITER ;\n'
        )
# 
#         @classmethod
#         def show_tables_selsert_st(cls, args:Sequence[Union[str, Tuple[str, Any]]]) -> str:
#             metadata = cls.metadata()
#             table_name = metadata.table_name
#             arg_sts = []
#             for arg in args:
#                 if isinstance(arg, str):
#                     st.append(f'v_{arg}')
#                 elif isinstance(arg, tuple) and len(arg) == 2:
#                     st.append()
# 
#             return f'selsert_{table_name}(\n  ' + ', \n  '.join(arg_sts) + ');\n'
#             



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
    
""" Schema data """

from dataclasses import dataclass
from db import dbtypes

from typing import Dict, Sequence, Tuple, Union


@dataclass
class Table:
    name: str
    columns: Dict[str, dbtypes.DataTypeBase]
    key_name: str
    fk_table: Dict[str, 'Table']

    @classmethod
    def show_create_table(self) -> str:
        return (
            f'CREATE TABLE `{self.name}`(\n  ' + ', \n  '.join((
                *(f'`{name}` {dt.sql_expr}' for name, dt in self.columns.items()),
                *(
                    f'FOREIGN KEY `fk_{name}` (`{name}`) REFERENCES `{t.name}`(`{t.key_name}`)'
                    for name, t in self.fk_table.items()
                ),
            )) + '\n);'
        )

    @classmethod
    def show_selsert(self) -> str:
        
        v_colnames = [name for name in self.columns if name != self.key_name]
            
        return ('DELIMITER //\n'
             + f'CREATE FUNCTION `selsert_{self.name}`(  \n'
             +  ', '.join(f'v_{name} {self.columns[name].info.dbtype}' for name in v_colnames)  # Arguments
             + f') RETURNS {self.columns[self.key_name].info.dbtype} DETERMINISTIC\n'           # Return type
             +  'BEGIN\n'
             + f'  @ret = (SELECT `{self.key_name}` FROM `{self.name}`\n'                       # Find existing record
             +  '    WHERE ' + ' AND '.join(f'`{name}` = v_{name}' for name in v_colnames) + ');\n' 
             +  '  IF @ret IS NOT NULL THEN\n'
             +  '    RETURN @ret;\n'                                                            # If found, return the record id
             +  '  END IF;\n'
             + f'  INSERT INTO `{self.key_name}`(' + ', '.join(f'`{name}`' for name in v_colnames) + ') \n'
             +  '    VALUES(' + ', '.join(f'v_{name}' for name in v_colnames) + ');\n'          # If not found, insert
             +  '  RETURN LAST_INSERT_ID();\n'                                                  #   and return the record id
             +  'END//\n'
             +  'DELIMITER ;\n'
        )


@dataclass
class SchemaData:
    """ Schema data class """
    tables:Dict[str, Table]



class ColsToGet:
    """ Configuration of column loading in table """
    def __init__(self,
        table:Table,
        _all:bool = False,
        **col_configs:Union[bool, 'ColsToGet'],
    ):
        """ Make configuration of column loading in table
            Set `_all` argument to `True` to get all columns (except linked other tables' columns).
            Use keyword arguments (keyword refers to column name) to specify individually.
            If `_all` are set to `True` and keyword argument(s) are set to `False`,
            get all columns except the column(s) specified in the keyword argument(s).
            In the case of columns which links to another table, specify ColsToGet recursively.

            Example (Assume `user` column links to `User` table):
            ColsToGet(True) : Load all columns
            ColsToGet(id=True, name=True) : Load `id` column and `name` column
            ColsToGet(True, name=False) : Load all columns except `name` column
            ColsToGet(user=ColsToGet(True)) : Load all columns in the `User` table
            ColsToGet(id=True, user=ColsToGet(id=True, name=True))
                 : Load `id` column, and `id` and `name` columns in the `User` table

        """
        target_colnames:Dict[str, Union[bool, Dict]] = {}
        if _all:
            for colname in table.columns:
                if not (colname in col_configs and not col_configs[colname]):
                    target_colnames[colname] = col_configs[colname]
        else:
            for colname in table.columns:
                if colname in col_configs and col_configs[colname]:
                    target_colnames[colname] = col_configs[colname]

        


        self.col_configs = col_configs


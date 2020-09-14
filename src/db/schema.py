""" Schema data """

from dataclasses import dataclass
from db import dbtypes

from typing import Dict


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

import mysql.connector as mydb

from typing import Union, Optional

class Cursor(mydb.cursor.MySQLCursor):
    def select(cls, *,
        where:str,
        order:List[Tuple[str, str]],
        count:int,
        offset:int,
        columns_to_load:Set[str],
    ) -> Iterator:
        """ Select records from the database """
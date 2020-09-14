import mysql.connector as mydb

from typing import Union, Optional

class TableLoadConfig:
    """ Configuration of column loading in table """
    def __init__(self,
        _all:Optional[bool] = None,
        **col_configs:Union[bool, 'TableLoadConfig'],
    ):
        """ Make configuration of column loading in table
            Set `_all` argument to `True` to get all columns (except linked other tables' columns).
            Use keyword arguments (keyword refers to column name) to specify individually.
            If `_all` are set to `True` and keyword argument(s) are set to `False`,
            get all columns except the column(s) specified in the keyword argument(s).
            In the case of columns which links to another table, set `True` to get all columns in that table, 
            or set TableLoadConfig recursively to specify individually.

            Example (Assume `user` column links to `User` table):
            TableLoadConfig(True) : Load all columns
            TableLoadConfig(id=True, name=True) : Load `id` column and `name` column
            TableLoadConfig(True, name=False) : Load all columns except `name` column
            TableLoadConfig(user=True) : Load all columns in the `User` table
            TableLoadConfig(id=True, user=TableLoadConfig(id=True, name=True))
                 : Load `id` column, and `id` and `name` columns in the `User` table

        """
        self.all = _all
        self.col_configs = col_configs



class Cursor(mydb.cursor.MySQLCursor):
    def select(cls, *,
        where:str,
        order:List[Tuple[str, str]],
        count:int,
        offset:int,
        columns_to_load:Set[str],
    ) -> Iterator:
        """ Select records from the database """
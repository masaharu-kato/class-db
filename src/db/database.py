import mysql.connector as mydb
from typing import Callable

class Database:
    """ Database class """
    def __init__(self, connector:Callable[[], mydb.MySQLConnection]):
        self.connector = connector
        self.conn = None
        self.tables

    def connect(self):
        self.conn = self.connector()

    def close_connection(self):
        self.conn.close()
        self.conn = None

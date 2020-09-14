import db.schema as dbs
import db.dbtypes as dbt

from typing import Optional, List

class ItemName(dbs.UniqueTable):
    """ """
    name: dbt.VarChar(128)

class Item(dbs.UniqueTable):
    """ """
    name: ItemName
    abstract: dbt.VarChar(256)

class Quantity(dbs.UniqueTable):
    """ """
    number: dbt.VarChar(32)
    unit: dbt.VarChar(16)

class Price(dbs.Table):
    """ """
    value: dbt.VarChar(32)
    source: dbt.VarChar(64)

class Record(dbs.UniqueTable):
    """ """
    item: Item
    quantity: Optional[Quantity]
    price: Optional[Price]
    sep_table: Optional['SeparatedTable']
    note: Optional[dbt.VarChar(128)]

class Subject(dbs.UniqueTable):
    """ """
    name: dbt.VarChar(64)
    sub_name: Optional[dbt.VarChar(64)]

class WorkKind(dbs.UniqueTable):
    """ """
    name: dbt.VarChar(32)

class Work(dbs.Table):
    """ """
    kind: WorkKind
    name: dbt.VarChar(128)

class DetailedTable(dbs.Table):
    """ """
    work: Work
    spot: dbt.VarChar(64)
    subject: Subject
    # records: List[Record]
    
class SeparatedTable(dbs.Table):
    """ """
    # records: List[Record]



def main():
    """ """
    dbs.create_tables(
        ItemName,
        Item,
        Quantity,
        Price,
        Record,
        Subject,
        WorkKind,
        Work,
        DetailedTable,
        SeparatedTable,
    )


if __name__ == "__main__":
    main()

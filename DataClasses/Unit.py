import datetime
import sqlite3

class Unit:
    """
    Class that provides the ability to interact with apartment unit objects Pythonically.
    """

    def __init__(self, unit_number: str, floor_plan_id: int, price: float, date_available: str="Now") -> None:
        self.unit_number = unit_number
        self.floor_plan_id = floor_plan_id # foreign key in FloorPlan table
        self.price = price
        self.date_of_update = datetime.date.today()
        self.composite_primary_key = f"{self.unit_number}_{self.date_of_update}"
        self.date_available = date_available

    
    def __str__(self) -> str:
        return f"\nUnit {self.unit_number} is ${self.price:.2f} as of {self.date_of_update}.  It will be available {self.date_available}."
    

    def __repr__(self) -> str:
        return self.__str__()
    

    def insert_into_sqlite(self, cursor: sqlite3.Cursor) -> None:
        """
        Inserts a Unit object into a SQLite database.
        """
        cursor.execute("SELECT 1 FROM Units WHERE unit_number=? AND date_of_update=?", (self.unit_number, self.date_of_update))
        if cursor.fetchone() is not None:
            return
        sql_statement = "INSERT INTO Units (unit_number, floor_plan_id, price, date_of_update, date_available) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(sql_statement, (self.unit_number, self.floor_plan_id, self.price, self.date_of_update, self.date_available))

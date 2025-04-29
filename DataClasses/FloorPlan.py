import sqlite3


class FloorPlan():
    def __init__(self, id: int, common_name: str, beds: float, baths: float, sq_ft: int, img_url: str="") -> None:
        self.floor_plan_id = id  # primary key
        self.name = common_name
        self.bedrooms = beds
        self.bathrooms = baths
        self.sq_ft = sq_ft
        self.img_url = img_url

        if self.bedrooms == round(self.bedrooms, 0):
            self.bedrooms = int(self.bedrooms)
        if self.bathrooms == round(self.bathrooms, 0):
            self.bathrooms = int(self.bathrooms)


    def __str__(self) -> str:
        return f"\nFloor Plan {self.name}:\t{self.bedrooms} bedrooms, {self.bathrooms} bathrooms, {self.sq_ft} sq.ft."
    

    def __repr__(self) -> str:
        return self.__str__()
        
    
    def get_id(self) -> int:
        """
        Returns the ID of the floor plan.
        """
        return self.floor_plan_id
    
    
    def insert_into_sqlite(self, cursor: sqlite3.Cursor) -> None:
        """
        Inserts a FloorPlan object into a SQLite table.
        """
        cursor.execute("SELECT 1 FROM FloorPlans WHERE floor_plan_id = ?", (self.floor_plan_id,))
        if cursor.fetchone() is not None:
            return
        sql_statement = "INSERT INTO FloorPlans (floor_plan_id, name, beds, baths, sq_ft, img_url) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.execute(sql_statement, (self.floor_plan_id, self.name, self.bedrooms, self.bathrooms, self.sq_ft, self.img_url))

def create_floor_plan_table(cursor: sqlite3.Cursor) -> None:
    """
    Creates the table for the floor plans if it doesn't exist.
    """
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS FloorPlans (
        floor_plan_id INTEGER PRIMARY KEY,
        name TEXT,
        beds REAL,
        baths REAL,
        sq_ft INTEGER,
        img_url TEXT
    )
    ''')
import sqlalchemy
from sqlalchemy import create_engine

# Create a SQLite database (file based)
DATABASE_URL = "postgresql+psycopg2://username:password@localhost:5432/mydb"

# Create engine
engine = create_engine(DATABASE_URL)

# Function to create table if not exists
def init_db():
    with engine.connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS school_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Zone TEXT,
            Grade TEXT,
            SKU TEXT,
            Book_Name TEXT,
            Book_Category TEXT,
            Qty INTEGER,
            Selling_Price REAL,
            Cost_Price REAL
        );
        """)

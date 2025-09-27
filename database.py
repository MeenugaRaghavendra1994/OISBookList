from sqlalchemy import create_engine
import urllib.parse

username = "postgres"
password = urllib.parse.quote_plus("Raghu@1819")  # Encodes @ as %40
host = "localhost"
port = "5432"
database = "school_books_db"

engine = create_engine(
    f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}",
    echo=True
)

# Function to create table if not exists
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
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
            )
        """))
        conn.commit()

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

# PostgreSQL connection
engine = create_engine(
    "postgresql+psycopg2://PostgreSQL 17:Raghu@1819@localhost:5432/school_books_db",
    echo=True
)

# Initialize database
def init_db():
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS school_books (
                id SERIAL PRIMARY KEY,
                Zone TEXT,
                Grade TEXT,
                SKU TEXT,
                Book_Name TEXT,
                Book_Category TEXT,
                Qty INTEGER,
                Selling_Price NUMERIC(12,2),
                Cost_Price NUMERIC(12,2)
            )
        """))
        conn.commit()

init_db()

st.title("School Book Management")

# Upload Excel and Store in DB
uploaded_file = st.file_uploader("Upload Excel", type=["xlsx"])

if uploaded_file is not None:
    try:
        # Read Excel as DataFrame
        df = pd.read_excel(uploaded_file, dtype=str)

        # Convert Qty, Selling Price, Cost Price to numeric
        for col in ["Qty", "Selling Price", "Cost Price"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # Insert data into PostgreSQL
        with engine.begin() as conn:  # Automatically commits or rollbacks
            for _, row in df.iterrows():
                conn.execute(text("""
                    INSERT INTO school_books 
                    (Zone, Grade, SKU, Book_Name, Book_Category, Qty, Selling_Price, Cost_Price)
                    VALUES (:Zone, :Grade, :SKU, :Book_Name, :Book_Category, :Qty, :Selling_Price, :Cost_Price)
                """), {
                    "Zone": row["Zone"],
                    "Grade": row["Grade"],
                    "SKU": row["SKU"],
                    "Book_Name": row["Book Name"],
                    "Book_Category": row["Book Category"],
                    "Qty": int(row["Qty"]),
                    "Selling_Price": float(row["Selling Price"]),
                    "Cost_Price": float(row["Cost Price"]),
                })
        st.success("✅ Data Imported into PostgreSQL Successfully!")

    except Exception as e:
        st.error(f"Error importing file: {e}")

# View data from PostgreSQL
if st.button("View Records"):
    with engine.connect() as conn:
        result = conn.execute(text("SELECT * FROM school_books"))
        data = result.fetchall()
        columns = result.keys()
        df = pd.DataFrame(data, columns=columns)
        st.dataframe(df, use_container_width=True)

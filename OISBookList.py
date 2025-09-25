import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import os

# ==============================
# DATABASE SETUP
# ==============================
DATABASE_URL = "sqlite:///books.db"  # Change to PostgreSQL or MySQL if needed
engine = create_engine(DATABASE_URL)

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

# Initialize DB on startup
init_db()

# ==============================
# HELPER FUNCTIONS
# ==============================
def load_data():
    query = "SELECT * FROM school_books"
    return pd.read_sql(query, engine)

def insert_record(record):
    df = pd.DataFrame([record])
    df.to_sql("school_books", engine, if_exists="append", index=False)

def update_record(record_id, updated_data):
    with engine.begin() as conn:
        conn.execute("""
            UPDATE school_books
            SET Zone = :Zone,
                Grade = :Grade,
                SKU = :SKU,
                Book_Name = :Book_Name,
                Book_Category = :Book_Category,
                Qty = :Qty,
                Selling_Price = :Selling_Price,
                Cost_Price = :Cost_Price
            WHERE id = :id
        """, {**updated_data, "id": record_id})

def delete_record(record_id):
    with engine.begin() as conn:
        conn.execute("DELETE FROM school_books WHERE id = :id", {"id": record_id})

# ==============================
# STREAMLIT UI
# ==============================
st.set_page_config(page_title="School Books Manager", layout="wide")

st.title("📚 School Books Management")

menu = st.sidebar.radio(
    "Menu",
    ["📘 Book List", "➕ Add Data", "✏️ Edit Data", "❌ Delete Data", "📥 Import/Export"]
)

# ==============================
# 1. VIEW BOOK LIST
# ==============================
if menu == "📘 Book List":
    st.subheader("School Book List")
    df = load_data()

    if df.empty:
        st.warning("No records available. Please add data first.")
    else:
        st.dataframe(df, use_container_width=True)

# ==============================
# 2. ADD NEW BOOK
# ==============================
elif menu == "➕ Add Data":
    st.subheader("Add New Book")

    with st.form("add_form"):
        zone = st.text_input("Zone")
        grade = st.text_input("Grade")
        sku = st.text_input("SKU")
        book_name = st.text_input("Book Name")
        category = st.text_input("Book Category")
        qty = st.number_input("Qty", min_value=1, value=1)
        selling = st.number_input("Selling Price", min_value=0.0, value=0.0)
        cost = st.number_input("Cost Price", min_value=0.0, value=0.0)

        submitted = st.form_submit_button("Add Book")

        if submitted:
            new_record = {
                "Zone": zone,
                "Grade": grade,
                "SKU": sku,
                "Book_Name": book_name,
                "Book_Category": category,
                "Qty": qty,
                "Selling_Price": selling,
                "Cost_Price": cost
            }
            insert_record(new_record)
            st.success("✅ Book Added Successfully!")

# ==============================
# 3. EDIT BOOK
# ==============================
elif menu == "✏️ Edit Data":
    st.subheader("Edit Book")

    df = load_data()
    if df.empty:
        st.warning("No records to edit.")
    else:
        record_id = st.selectbox("Select Record ID", df["id"].tolist())
        row = df[df["id"] == record_id].iloc[0]

        with st.form("edit_form"):
            zone = st.text_input("Zone", row["Zone"])
            grade = st.text_input("Grade", row["Grade"])
            sku = st.text_input("SKU", row["SKU"])
            book_name = st.text_input("Book Name", row["Book_Name"])
            category = st.text_input("Book Category", row["Book_Category"])
            qty = st.number_input("Qty", min_value=1, value=int(row["Qty"]))
            selling = st.number_input("Selling Price", min_value=0.0, value=float(row["Selling_Price"]))
            cost = st.number_input("Cost Price", min_value=0.0, value=float(row["Cost_Price"]))
            
            submitted = st.form_submit_button("Update Book")

            if submitted:
                updated_data = {
                    "Zone": zone,
                    "Grade": grade,
                    "SKU": sku,
                    "Book_Name": book_name,
                    "Book_Category": category,
                    "Qty": qty,
                    "Selling_Price": selling,
                    "Cost_Price": cost
                }
                update_record(record_id, updated_data)
                st.success("✅ Book Updated Successfully!")

# ==============================
# 4. DELETE BOOK
# ==============================
elif menu == "❌ Delete Data":
    st.subheader("Delete Book")

    df = load_data()
    if df.empty:
        st.warning("No records to delete.")
    else:
        record_id = st.selectbox("Select Record ID to Delete", df["id"].tolist())

        if st.button("Delete"):
            delete_record(record_id)
            st.success("✅ Book Deleted Successfully!")

# ==============================
# 5. IMPORT / EXPORT
# ==============================
elif menu == "📥 Import/Export":
    st.subheader("Import / Export Excel")

    # ---------- IMPORT ----------
    uploaded_file = st.file_uploader("📥 Upload Excel File", type=["xlsx"])
    if uploaded_file:
        try:
            imported_df = pd.read_excel(uploaded_file, dtype=str)

            required_columns = [
                "Zone", "Grade", "SKU", "Book Name", "Book Category",
                "Qty", "Selling Price", "Cost Price"
            ]
            missing_cols = [col for col in required_columns if col not in imported_df.columns]

            if missing_cols:
                st.error(f"❌ Missing columns: {', '.join(missing_cols)}")
            else:
                numeric_cols = ["Qty", "Selling Price", "Cost Price"]
                for col in numeric_cols:
                    imported_df[col] = pd.to_numeric(imported_df[col], errors="coerce").fillna(0)

                for _, row in imported_df.iterrows():
                    insert_record({
                        "Zone": row["Zone"],
                        "Grade": row["Grade"],
                        "SKU": row["SKU"],
                        "Book_Name": row["Book Name"],
                        "Book_Category": row["Book Category"],
                        "Qty": row["Qty"],
                        "Selling_Price": row["Selling Price"],
                        "Cost_Price": row["Cost Price"]
                    })

                st.success("✅ Data Imported Successfully!")
                st.dataframe(imported_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error importing file: {e}")

    # ---------- EXPORT ----------
    if st.button("📤 Export to Excel"):
        df_export = load_data()
        export_path = "School_Book_List.xlsx"
        df_export.to_excel(export_path, index=False, engine="openpyxl")

        with open(export_path, "rb") as file:
            st.download_button(
                label="Download Excel",
                data=file,
                file_name="School_Book_List.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

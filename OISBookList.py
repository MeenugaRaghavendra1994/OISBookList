import streamlit as st
import pandas as pd
import plotly.express as px

# ---------- Initialize Data ----------
if "data" not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Zone", "Grade", "SKU", "Book Name", "Book Category",
        "Qty", "Selling Price", "Cost Price"
    ])

# ---------- Helper Functions ----------
def calculate_metrics(df):
    if df.empty:
        return df
    df["Total Cost"] = df["Qty"] * df["Cost Price"]
    df["Total Selling"] = df["Qty"] * df["Selling Price"]
    df["Margin"] = df["Total Selling"] - df["Total Cost"]
    df["Margin %"] = (df["Margin"] / df["Total Selling"]).round(2) * 100
    return df

# ---------- Sidebar Menu ----------
menu = st.sidebar.radio(
    "Menu", 
    ["📘 Book List", "➕ Add Data", "✏️ Edit Data", "❌ Delete Data", "📊 Dashboard", "📥 Import/Export"]
)

# ---------- Book List ----------
if menu == "📘 Book List":
    st.subheader("School Book List")
    df = calculate_metrics(st.session_state.data.copy())
    st.dataframe(df, use_container_width=True)

# ---------- Add Data ----------
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
            new_row = {
                "Zone": zone, "Grade": grade, "SKU": sku, "Book Name": book_name,
                "Book Category": category, "Qty": qty,
                "Selling Price": selling, "Cost Price": cost
            }
            st.session_state.data = pd.concat(
                [st.session_state.data, pd.DataFrame([new_row])], ignore_index=True
            )
            st.success("✅ Book Added Successfully!")

# ---------- Edit Data ----------
elif menu == "✏️ Edit Data":
    st.subheader("Edit Book")
    if len(st.session_state.data) == 0:
        st.warning("No records to edit.")
    else:
        index = st.number_input(
            "Enter Row Index to Edit (0-based)", 
            min_value=0, max_value=len(st.session_state.data)-1
        )
        row = st.session_state.data.loc[index]

        with st.form("edit_form"):
            zone = st.text_input("Zone", row["Zone"])
            grade = st.text_input("Grade", row["Grade"])
            sku = st.text_input("SKU", row["SKU"])
            book_name = st.text_input("Book Name", row["Book Name"])
            category = st.text_input("Book Category", row["Book Category"])
            qty = st.number_input("Qty", min_value=1, value=int(row["Qty"]))
            selling = st.number_input("Selling Price", min_value=0.0, value=float(row["Selling Price"]))
            cost = st.number_input("Cost Price", min_value=0.0, value=float(row["Cost Price"]))
            submitted = st.form_submit_button("Update Book")

            if submitted:
                st.session_state.data.loc[index] = [
                    zone, grade, sku, book_name, category, qty, selling, cost
                ]
                st.success("✅ Book Updated Successfully!")

# ---------- Delete Data ----------
elif menu == "❌ Delete Data":
    st.subheader("Delete Book")
    if len(st.session_state.data) == 0:
        st.warning("No records to delete.")
    else:
        index = st.number_input(
            "Enter Row Index to Delete (0-based)", 
            min_value=0, max_value=len(st.session_state.data)-1
        )
        if st.button("Delete"):
            st.session_state.data = st.session_state.data.drop(index).reset_index(drop=True)
            st.success("✅ Book Deleted Successfully!")

# ---------- Dashboard ----------
elif menu == "📊 Dashboard":
    st.subheader("Dashboard & Filters")

    df = calculate_metrics(st.session_state.data.copy())

    if df.empty:
        st.warning("No data available for dashboard.")
    else:
        # Filters
        zone_filter = st.multiselect("Filter by Zone", options=df["Zone"].unique())
        grade_filter = st.multiselect("Filter by Grade", options=df["Grade"].unique())
        category_filter = st.multiselect("Filter by Category", options=df["Book Category"].unique())

        if zone_filter:
            df = df[df["Zone"].isin(zone_filter)]
        if grade_filter:
            df = df[df["Grade"].isin(grade_filter)]
        if category_filter:
            df = df[df["Book Category"].isin(category_filter)]

        st.dataframe(df, use_container_width=True)

        # Summary Metrics
        st.write("### Summary")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Qty", int(df["Qty"].sum()))
        col2.metric("Total Cost", round(df["Total Cost"].sum(), 2))
        col3.metric("Total Selling", round(df["Total Selling"].sum(), 2))
        col4.metric("Total Margin", round(df["Margin"].sum(), 2))

        st.divider()

        # Charts
        st.write("### Visual Insights")

        # Sales by Zone
        fig_zone = px.bar(df.groupby("Zone")[["Total Selling", "Margin"]].sum().reset_index(),
                          x="Zone", y=["Total Selling", "Margin"], barmode="group",
                          title="Sales & Margin by Zone")
        st.plotly_chart(fig_zone, use_container_width=True)

        # Sales by Grade
        fig_grade = px.bar(df.groupby("Grade")[["Total Selling"]].sum().reset_index(),
                           x="Grade", y="Total Selling", color="Grade",
                           title="Sales by Grade")
        st.plotly_chart(fig_grade, use_container_width=True)

        # Margin by Category (Pie Chart)
        fig_cat = px.pie(df, names="Book Category", values="Margin", 
                         title="Margin Contribution by Category")
        st.plotly_chart(fig_cat, use_container_width=True)

# ---------- Import/Export ----------
elif menu == "📥 Import/Export":
    st.subheader("Import / Export Excel")

    # Export
    if st.button("📤 Export to Excel"):
        df_export = calculate_metrics(st.session_state.data.copy())
        file_path = "School_Book_List.xlsx"
        df_export.to_excel(file_path, index=False)
        st.download_button(
            label="Download Excel File",
            data=open(file_path, "rb").read(),
            file_name=file_path,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    # ---------- Import ----------
uploaded_file = st.file_uploader("📥 Upload Excel File", type=["xlsx"])

if uploaded_file:
    # Read all columns as strings initially
    imported_df = pd.read_excel(uploaded_file, dtype=str)

    # Convert numeric columns back to numbers safely
    numeric_cols = ["Qty", "Selling Price", "Cost Price"]
    for col in numeric_cols:
        if col in imported_df.columns:
            imported_df[col] = pd.to_numeric(imported_df[col], errors="coerce").fillna(0)

    # Store in session state
    st.session_state.data = imported_df

    st.success("✅ Data Imported Successfully!")
    st.dataframe(imported_df, use_container_width=True)

        # ---------- Book List with Filters & Download ----------
if menu == "📘 Book List":
    st.subheader("School Book List with Filters")

    df = calculate_metrics(st.session_state.data.copy())

    if df.empty:
        st.warning("No data available. Please add records first.")
    else:
        st.write("### Apply Filters")

        # Create a two-column layout for filters
        col1, col2 = st.columns(2)

        # Text filters
        with col1:
            zone_filter = st.multiselect("Zone", options=df["Zone"].unique())
            grade_filter = st.multiselect("Grade", options=df["Grade"].unique())
            category_filter = st.multiselect("Book Category", options=df["Book Category"].unique())

        with col2:
            sku_filter = st.text_input("Search SKU (partial match)")
            book_name_filter = st.text_input("Search Book Name (partial match)")

        # Numeric filters
        qty_min, qty_max = int(df["Qty"].min()), int(df["Qty"].max())
        selling_min, selling_max = float(df["Selling Price"].min()), float(df["Selling Price"].max())
        cost_min, cost_max = float(df["Cost Price"].min()), float(df["Cost Price"].max())

        st.write("### Numeric Filters")
        qty_range = st.slider("Quantity Range", min_value=qty_min, max_value=qty_max, value=(qty_min, qty_max))
        selling_range = st.slider("Selling Price Range", min_value=selling_min, max_value=selling_max,
                                  value=(selling_min, selling_max))
        cost_range = st.slider("Cost Price Range", min_value=cost_min, max_value=cost_max,
                               value=(cost_min, cost_max))

        # ---------- Apply Filters ----------
        filtered_df = df.copy()

        if zone_filter:
            filtered_df = filtered_df[filtered_df["Zone"].isin(zone_filter)]
        if grade_filter:
            filtered_df = filtered_df[filtered_df["Grade"].isin(grade_filter)]
        if category_filter:
            filtered_df = filtered_df[filtered_df["Book Category"].isin(category_filter)]
        if sku_filter:
            filtered_df = filtered_df[filtered_df["SKU"].str.contains(sku_filter, case=False, na=False)]
        if book_name_filter:
            filtered_df = filtered_df[filtered_df["Book Name"].str.contains(book_name_filter, case=False, na=False)]

        # Numeric filters
        filtered_df = filtered_df[
            (filtered_df["Qty"].between(qty_range[0], qty_range[1])) &
            (filtered_df["Selling Price"].between(selling_range[0], selling_range[1])) &
            (filtered_df["Cost Price"].between(cost_range[0], cost_range[1]))
        ]

        # ---------- Display Filtered Data ----------
        st.write(f"### Filtered Records: {len(filtered_df)}")
        st.dataframe(filtered_df, use_container_width=True)

        # ---------- Download Filtered Data ----------
        if not filtered_df.empty:
            export_file = "Filtered_Book_List.xlsx"
            filtered_df.to_excel(export_file, index=False)

            with open(export_file, "rb") as file:
                st.download_button(
                    label="📥 Download Filtered Data",
                    data=file,
                    file_name=export_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

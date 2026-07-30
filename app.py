import pandas as pd
import streamlit as st


# --------------------------------------------------
# 1. PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------
# 2. DASHBOARD TITLE
# --------------------------------------------------

st.title("📊 Retail Sales Dashboard")

st.write(
    "Analyse sales, orders, products and categories "
    "using Python, Pandas and Streamlit."
)


# --------------------------------------------------
# 3. LOAD THE CSV DATASET
# --------------------------------------------------

try:
    df = pd.read_csv("sales_data.csv")

except FileNotFoundError:
    st.error(
        "sales_data.csv was not found. "
        "Make sure it is inside the same folder as app.py."
    )
    st.stop()


# --------------------------------------------------
# 4. CHECK REQUIRED COLUMNS
# --------------------------------------------------

required_columns = [
    "OrderID",
    "Date",
    "Product",
    "Category",
    "Quantity",
    "UnitPrice",
    "TotalSales",
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    st.error(
        f"These columns are missing from the CSV file: "
        f"{missing_columns}"
    )
    st.stop()


# --------------------------------------------------
# 5. CLEAN THE DATA
# --------------------------------------------------

# Convert Date into a proper date format
df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce",
)

# Convert numeric columns into numbers
numeric_columns = [
    "Quantity",
    "UnitPrice",
    "TotalSales",
]

for column in numeric_columns:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )

# Remove duplicate rows
df = df.drop_duplicates()

# Remove rows with missing important values
df = df.dropna(
    subset=[
        "OrderID",
        "Product",
        "Category",
        "Quantity",
        "UnitPrice",
        "TotalSales",
    ]
)


# --------------------------------------------------
# 6. SIDEBAR FILTERS
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

# Category options
category_options = sorted(
    df["Category"]
    .dropna()
    .unique()
    .tolist()
)

# Category selection
selected_categories = st.sidebar.multiselect(
    "Select Categories",
    options=category_options,
    default=category_options,
)

# Products belonging to the selected categories
product_options = sorted(
    df[
        df["Category"].isin(selected_categories)
    ]["Product"]
    .dropna()
    .unique()
    .tolist()
)

# Product selection
selected_products = st.sidebar.multiselect(
    "Select Products",
    options=product_options,
    default=product_options,
)

# Apply category and product filters
filtered_df = df[
    (df["Category"].isin(selected_categories))
    & (df["Product"].isin(selected_products))
].copy()


# Stop when no data is selected
if filtered_df.empty:
    st.warning(
        "No records match the selected filters. "
        "Please select at least one category and product."
    )
    st.stop()


# --------------------------------------------------
# 7. MAIN CALCULATIONS
# --------------------------------------------------

total_sales = filtered_df["TotalSales"].sum()

total_orders = filtered_df["OrderID"].nunique()

items_sold = filtered_df["Quantity"].sum()

average_order = (
    total_sales / total_orders
    if total_orders > 0
    else 0
)


# --------------------------------------------------
# 8. SUMMARY CARDS
# --------------------------------------------------

st.subheader("Sales Summary")

column1, column2, column3, column4 = st.columns(4)

column1.metric(
    label="Total Sales",
    value=f"Rs. {total_sales:,.2f}",
)

column2.metric(
    label="Total Orders",
    value=f"{total_orders:,}",
)

column3.metric(
    label="Items Sold",
    value=f"{items_sold:,.0f}",
)

column4.metric(
    label="Average Order",
    value=f"Rs. {average_order:,.2f}",
)

st.divider()


# --------------------------------------------------
# 9. PREPARE SALES ANALYSIS
# --------------------------------------------------

# Sales by category
category_sales = (
    filtered_df
    .groupby("Category")["TotalSales"]
    .sum()
    .sort_values(ascending=False)
)

# Sales by product
product_sales = (
    filtered_df
    .groupby("Product")["TotalSales"]
    .sum()
    .sort_values(ascending=False)
)

# Quantity sold by product
product_quantity = (
    filtered_df
    .groupby("Product")["Quantity"]
    .sum()
    .sort_values(ascending=False)
)


# --------------------------------------------------
# 10. CATEGORY AND PRODUCT CHARTS
# --------------------------------------------------

left_column, right_column = st.columns(2)

with left_column:

    st.subheader("Sales by Category")

    st.bar_chart(
        category_sales,
        use_container_width=True,
    )


with right_column:

    st.subheader("Sales by Product")

    st.bar_chart(
        product_sales,
        use_container_width=True,
    )


# --------------------------------------------------
# 11. MONTHLY SALES CHART
# --------------------------------------------------

st.subheader("Monthly Sales Trend")

monthly_data = filtered_df.dropna(
    subset=["Date"]
).copy()

if not monthly_data.empty:

    monthly_data["Month"] = (
        monthly_data["Date"]
        .dt.to_period("M")
        .dt.to_timestamp()
    )

    monthly_sales = (
        monthly_data
        .groupby("Month")["TotalSales"]
        .sum()
        .sort_index()
    )

    st.line_chart(
        monthly_sales,
        use_container_width=True,
    )

else:
    st.warning(
        "No valid dates are available for monthly analysis."
    )


# --------------------------------------------------
# 12. IMPORTANT FINDINGS
# --------------------------------------------------

st.subheader("Important Findings")

top_product = product_sales.idxmax()
top_product_sales = product_sales.max()

top_category = category_sales.idxmax()
top_category_sales = category_sales.max()

most_sold_product = product_quantity.idxmax()
most_sold_quantity = product_quantity.max()

finding1, finding2, finding3 = st.columns(3)

with finding1:
    st.success(
        f"""
        **Top Product**

        {top_product}

        Sales: Rs. {top_product_sales:,.2f}
        """
    )

with finding2:
    st.success(
        f"""
        **Top Category**

        {top_category}

        Sales: Rs. {top_category_sales:,.2f}
        """
    )

with finding3:
    st.success(
        f"""
        **Most Sold Product**

        {most_sold_product}

        Quantity: {most_sold_quantity:,.0f}
        """
    )


# --------------------------------------------------
# 13. PRODUCT SUMMARY TABLE
# --------------------------------------------------

st.subheader("Product Summary")

product_summary = (
    filtered_df
    .groupby("Product")
    .agg(
        TotalQuantity=("Quantity", "sum"),
        AveragePrice=("UnitPrice", "mean"),
        TotalSales=("TotalSales", "sum"),
        TotalOrders=("OrderID", "nunique"),
    )
    .reset_index()
    .sort_values(
        by="TotalSales",
        ascending=False,
    )
)

product_summary["AveragePrice"] = (
    product_summary["AveragePrice"].round(2)
)

product_summary["TotalSales"] = (
    product_summary["TotalSales"].round(2)
)

st.dataframe(
    product_summary,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# 14. SALES RECORDS
# --------------------------------------------------

st.subheader("Sales Records")

st.write(
    f"Showing {len(filtered_df):,} sales records."
)

search_text = st.text_input(
    "Search Product or Category",
    placeholder="For example: Laptop or Electronics",
)

displayed_df = filtered_df.copy()

if search_text:

    search_text = search_text.lower()

    displayed_df = displayed_df[
        displayed_df["Product"]
        .astype(str)
        .str.lower()
        .str.contains(search_text, na=False)
        |
        displayed_df["Category"]
        .astype(str)
        .str.lower()
        .str.contains(search_text, na=False)
    ]

st.dataframe(
    displayed_df,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# 15. DOWNLOAD FILTERED DATA
# --------------------------------------------------

download_data = displayed_df.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="⬇️ Download Filtered Data",
    data=download_data,
    file_name="filtered_sales_data.csv",
    mime="text/csv",
)


# --------------------------------------------------
# 16. DATASET INFORMATION
# --------------------------------------------------

st.divider()

st.subheader("Dataset Information")

information1, information2, information3 = st.columns(3)

information1.metric(
    "Dataset Rows",
    f"{len(df):,}",
)

information2.metric(
    "Dataset Columns",
    len(df.columns),
)

information3.metric(
    "Duplicate Rows Removed",
    f"{df.duplicated().sum():,}",
)

with st.expander("View Column Information"):

    column_information = pd.DataFrame(
        {
            "Column": df.columns,
            "Data Type": [
                str(data_type)
                for data_type in df.dtypes
            ],
            "Missing Values": [
                int(df[column].isnull().sum())
                for column in df.columns
            ],
        }
    )

    st.dataframe(
        column_information,
        use_container_width=True,
        hide_index=True,
    )


# --------------------------------------------------
# 17. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Retail Sales Dashboard | "
    "Created with Python, Pandas and Streamlit"
)
import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
import base64
import os
from datetime import datetime

# Set page config
st.set_page_config(page_title="InsightEdge: BI Dashboard", layout="wide")

# Title and description
st.title("📊 InsightEdge: Business Intelligence Dashboard - Sales Insights")
st.markdown("Upload your JSON, CSV, or Excel sales data file to generate an interactive dashboard.")

# Dark/Light mode toggle
if 'theme' not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    if st.session_state.theme == "light":
        st.session_state.theme = "dark"
    else:
        st.session_state.theme = "light"

st.button("Toggle Dark/Light Mode", on_click=toggle_theme)

# File uploader
uploaded_file = st.file_uploader("📂 Choose a JSON, CSV, or Excel file", type=["json", "csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith("json"):
            df = pd.read_json(uploaded_file)
        elif uploaded_file.name.endswith("csv"):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith("xlsx"):
            df = pd.read_excel(uploaded_file)

        df["Date"] = pd.to_datetime(df["Date"])

        # Sidebar filters (✅ FIXED DATE FILTER SECTION)
        st.sidebar.header("Filters")
        min_date = df["Date"].min()
        max_date = df["Date"].max()
        date_range = st.sidebar.date_input("Select date range", [min_date, max_date], 
                                           min_value=min_date, max_value=max_date)

        start_date = pd.to_datetime(date_range[0])
        end_date = pd.to_datetime(date_range[1])

        product_filter = st.sidebar.multiselect("Filter by Product", options=df["Product"].unique(), default=df["Product"].unique())
        state_filter = st.sidebar.multiselect("Filter by State", options=df["State"].unique(), default=df["State"].unique())

        # Apply filters
        df_filtered = df[(df["Date"] >= start_date) & (df["Date"] <= end_date) &
                         (df["Product"].isin(product_filter)) &
                         (df["State"].isin(state_filter))]

        # Show raw data
        with st.expander("📋 Raw Data Preview"):
            st.dataframe(df_filtered)

        # KPI tiles
        total_sales = df_filtered["Total Price"].sum()
        total_orders = df_filtered.shape[0]
        best_product = df_filtered.groupby("Product")["Total Price"].sum().idxmax()
        top_state = df_filtered.groupby("State")["Total Price"].sum().idxmax()

        st.markdown(f"### Total Sales: 💰 {total_sales:,.2f}")
        st.markdown(f"### Total Orders: 🛒 {total_orders}")
        st.markdown(f"### Best Selling Product: {best_product}")
        st.markdown(f"### Top State by Revenue: {top_state}")

        # First row: Sales by Product & Sales Over Time
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df_filtered, x="Product", y="Total Price", title="💼 Sales by Product", color="Product")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            df_sorted = df_filtered.sort_values("Date")
            fig2 = px.line(df_sorted, x="Date", y="Total Price", title="📈 Sales Over Time", markers=True)
            st.plotly_chart(fig2, use_container_width=True)

        # Second row: Sales by Channel & Payment Methods
        col3, col4 = st.columns(2)
        with col3:
            fig3 = px.pie(df_filtered, names="Sales Channel", values="Total Price", title="🛍️ Sales by Channel")
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            fig4 = px.pie(df_filtered, names="Payment Method", values="Total Price", title="💳 Payment Methods")
            st.plotly_chart(fig4, use_container_width=True)

        # Full width: Sales by State
        fig5 = px.bar(df_filtered, x="State", y="Total Price", title="🌍 Sales by State", color="State")
        st.plotly_chart(fig5, use_container_width=True)

        # Export options
        st.sidebar.header("Export Data")
        
        def convert_df(df):
            return df.to_csv(index=False).encode('utf-8')

        csv = convert_df(df_filtered)
        st.sidebar.download_button("Download CSV", csv, "filtered_data.csv", "text/csv")

        # PNG download for charts
        def get_image(fig):
            img_bytes = fig.to_image(format="png")
            return base64.b64encode(img_bytes).decode()

        fig1_image = get_image(fig1)
        st.sidebar.markdown(f"![Sales by Product](data:image/png;base64,{fig1_image})")

    except Exception as e:
        st.error(f"🚫 Error loading file: {e}")

else:
    st.info("📁 Please upload a valid JSON, CSV, or Excel file to get started.")

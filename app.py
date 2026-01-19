import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO

st.set_page_config(
    page_title="E-Commerce Business Intelligence Dashboard",
    page_icon="📊",
    layout="wide"
)


# ==================== LOAD & CLEAN DATA ====================
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/carrie1/ecommerce-data/master/data.csv"
    response = requests.get(url)
    csv_data = StringIO(response.text)

    data = pd.read_csv(csv_data, encoding="ISO-8859-1")
    strategy = pd.read_csv("marketing_strategy_recommendations.csv")

    # CLEANING
    data.columns = data.columns.str.strip()
    data = data[data["Quantity"] > 0]
    data = data[data["UnitPrice"] > 0]
    data = data[~data["InvoiceNo"].astype(str).str.startswith("C")]

    # FEATURE ENGINEERING
    data["TotalPrice"] = data["Quantity"] * data["UnitPrice"]
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["Month"] = data["InvoiceDate"].dt.to_period("M").astype(str)

    return data, strategy

data, strategy = load_data()

# ==================== TITLE ====================
st.title("🚀 E-Commerce Business Intelligence Dashboard (PRO)")
st.markdown("""
**CRISP-DM Deployment | Business Analytics | Marketing Strategy**
""")

# ==================== SIDEBAR FILTERS ====================
st.sidebar.header("🎯 Smart Filters")

countries = sorted(data["Country"].dropna().unique())
selected_country = st.sidebar.multiselect(
    "🌍 Select Country",
    options=countries,
    default=["United Kingdom"] if "United Kingdom" in countries else []
)

if selected_country:
    data = data[data["Country"].isin(selected_country)]

# ==================== KPI SECTION ====================
st.header("📌 Key Business KPIs")

total_sales = float(data["TotalPrice"].sum())
num_customers = data["CustomerID"].nunique()
num_orders = data["InvoiceNo"].nunique()
avg_order_value = total_sales / num_orders if num_orders > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"{total_sales:,.2f}")
col2.metric("👥 Active Customers", num_customers)
col3.metric("🧾 Total Orders", num_orders)
col4.metric("📦 Avg Order Value", f"{avg_order_value:,.2f}")

# ==================== SALES OVER TIME (PRO) ====================
st.subheader("📈 Revenue Trend (Monthly)")

sales_time = (
    data.groupby("Month")["TotalPrice"]
    .sum()
    .reset_index()
)

fig_trend = px.line(
    sales_time,
    x="Month",
    y="TotalPrice",
    title="Monthly Revenue Evolution"
)
st.plotly_chart(fig_trend, use_container_width=True)

# ==================== TOP PRODUCTS ====================
st.subheader("🛍️ Top 10 Products by Revenue")

top_products = (
    data.groupby("Description")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_products = px.bar(
    top_products,
    x="TotalPrice",
    y="Description",
    orientation="h",
    title="Top Selling Products"
)
st.plotly_chart(fig_products, use_container_width=True)

# ==================== TOP CUSTOMERS ====================
st.subheader("👑 Top 10 Customers (VIP)")

top_customers = (
    data.groupby("CustomerID")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_customers = px.bar(
    top_customers,
    x="CustomerID",
    y="TotalPrice",
    title="Top Customers by Spending"
)
st.plotly_chart(fig_customers, use_container_width=True)

# ==================== COUNTRY REVENUE MAP ====================
st.subheader("🌍 Revenue by Country")

country_sales = (
    data.groupby("Country")["TotalPrice"]
    .sum()
    .reset_index()
)

fig_map = px.choropleth(
    country_sales,
    locations="Country",
    locationmode="country names",
    color="TotalPrice",
    title="Revenue Distribution by Country"
)
st.plotly_chart(fig_map, use_container_width=True)

# ==================== RFM ANALYSIS (PRO FEATURE) ====================
st.subheader("⭐ Customer Segmentation (RFM)")

rfm = (
    data.groupby("CustomerID")
    .agg({
        "InvoiceDate": "max",
        "InvoiceNo": "nunique",
        "TotalPrice": "sum"
    })
    .reset_index()
)

rfm.columns = ["CustomerID", "LastPurchase", "Frequency", "Monetary"]

rfm["Recency"] = (pd.Timestamp.now() - rfm["LastPurchase"]).dt.days

st.dataframe(rfm.head(20), use_container_width=True)

# ==================== MARKETING STRATEGY ====================
st.subheader("🎯 Marketing Strategy Dashboard")
st.dataframe(strategy, use_container_width=True)

fig_strategy = px.bar(
    strategy,
    x="Segment",
    y="Priority_Score",
    title="Marketing Priority by Segment"
)
st.plotly_chart(fig_strategy, use_container_width=True)

st.success("🔥 PRO Dashboard Live — Business Ready")

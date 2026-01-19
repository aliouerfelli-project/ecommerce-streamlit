import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from io import StringIO

# ============ CONFIG ============
st.set_page_config(
    page_title="E-Commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)

# ============ LOAD DATA ============
@st.cache_data
def load_data():
    # نحمّلو الداتا بطريقة يقبلها Streamlit Cloud
    url = "https://raw.githubusercontent.com/carrie1/ecommerce-data/master/data.csv"
    
    # تحميل الملف كـ text أولاً (يتجاوز القيود)
    response = requests.get(url)
    csv_data = StringIO(response.text)
    
    data = pd.read_csv(csv_data, encoding="ISO-8859-1")
    strategy = pd.read_csv("marketing_strategy_recommendations.csv")

    # Cleaning & Feature Engineering
    data = data.dropna(subset=["CustomerID", "Quantity", "UnitPrice"])
    data["TotalPrice"] = data["Quantity"] * data["UnitPrice"]

    if "InvoiceDate" in data.columns:
        data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")

    return data, strategy

data, strategy = load_data()

# ============ TITLE ============
st.title("📊 E-Commerce Analytics Dashboard")
st.markdown("**CRISP-DM | Business Analytics & Marketing Strategy Deployment**")

# ============ SIDEBAR FILTERS ============
st.sidebar.header("🔍 Filters")

if "Country" in data.columns:
    selected_country = st.sidebar.multiselect(
        "Select Country",
        options=data["Country"].dropna().unique(),
        default=list(data["Country"].dropna().unique()[:3])
    )
    data = data[data["Country"].isin(selected_country)]

# ============ KPIs ============
st.header("📌 Key Performance Indicators")

total_sales = data["TotalPrice"].sum()
num_customers = data["CustomerID"].nunique()
avg_basket = total_sales / num_customers
avg_order_value = data.groupby("InvoiceNo")["TotalPrice"].sum().mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Sales", f"{total_sales:,.2f}")
col2.metric("👥 Customers", num_customers)
col3.metric("🛒 Avg Basket", f"{avg_basket:,.2f}")
col4.metric("📦 Avg Order Value", f"{avg_order_value:,.2f}")

# ============ TOP PRODUCTS ============
st.subheader("🛍️ Top 10 Products by Sales")

top_products = (
    data.groupby("Description")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig1 = px.bar(
    top_products,
    x="TotalPrice",
    y="Description",
    orientation="h",
    title="Top 10 Products"
)
st.plotly_chart(fig1, use_container_width=True)

# ============ SALES OVER TIME ============
if "InvoiceDate" in data.columns:
    st.subheader("📈 Monthly Sales Trend")

    sales_time = (
        data.set_index("InvoiceDate")
        .resample("M")["TotalPrice"]
        .sum()
        .reset_index()
    )

    fig2 = px.line(
        sales_time,
        x="InvoiceDate",
        y="TotalPrice",
        title="Monthly Sales"
    )
    st.plotly_chart(fig2, use_container_width=True)

# ============ TOP CUSTOMERS ============
st.subheader("👥 Top 10 Customers")

top_customers = (
    data.groupby("CustomerID")["TotalPrice"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig3 = px.bar(
    top_customers,
    x="CustomerID",
    y="TotalPrice",
    title="Top 10 Customers"
)
st.plotly_chart(fig3, use_container_width=True)

# ============ MARKETING STRATEGY ============
st.subheader("🎯 Marketing Strategy Recommendations")
st.dataframe(strategy, use_container_width=True)

fig4 = px.bar(
    strategy,
    x="Segment",
    y="Priority_Score",
    title="Marketing Strategy Priorities"
)
st.plotly_chart(fig4, use_container_width=True)

st.success("🚀 Live Dashboard Ready")

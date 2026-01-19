import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="E-Commerce Dashboard",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_data():
    # نقرّيو الداتا المصغّرة اللي حطّيتها في GitHub
    data = pd.read_csv("data_small.csv", encoding="ISO-8859-1")
    strategy = pd.read_csv("marketing_strategy_recommendations.csv")

    # تنظيف الداتا
    data = data.dropna(subset=["CustomerID", "Quantity", "UnitPrice"])

    # فلترة القيم السالبة
    data = data[data["Quantity"] > 0]
    data = data[data["UnitPrice"] > 0]

    # حذف الفواتير الملغاة (اللي تبدأ بـ C)
    data = data[~data["InvoiceNo"].astype(str).str.startswith("C")]

    # إنشاء عمود المبيعات الإجمالية
    data["TotalPrice"] = data["Quantity"] * data["UnitPrice"]

    # تحويل التاريخ واستخراج الشهر
    data["InvoiceDate"] = pd.to_datetime(data["InvoiceDate"], errors="coerce")
    data["Month"] = data["InvoiceDate"].dt.to_period("M").astype(str)

    return data, strategy

# ===== تحميل البيانات =====
data, strategy = load_data()

# ===== العنوان =====
st.title("📊 E-Commerce Business Intelligence Dashboard")

# ===== KPI Cards =====
total_sales = data["TotalPrice"].sum()
total_orders = data["InvoiceNo"].nunique()
total_customers = data["CustomerID"].nunique()
avg_order_value = total_sales / total_orders

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Sales", f"£{total_sales:,.2f}")
col2.metric("📦 Total Orders", f"{total_orders:,}")
col3.metric("👥 Total Customers", f"{total_customers:,}")
col4.metric("📈 Avg Order Value", f"£{avg_order_value:,.2f}")

st.markdown("---")

# ===== Sidebar Filters =====
st.sidebar.header("🔎 Filters")

country = st.sidebar.multiselect(
    "Select Country",
    options=sorted(data["Country"].dropna().unique()),
    default=None
)

month = st.sidebar.multiselect(
    "Select Month",
    options=sorted(data["Month"].dropna().unique()),
    default=None
)

filtered_data = data.copy()

if country:
    filtered_data = filtered_data[filtered_data["Country"].isin(country)]

if month:
    filtered_data = filtered_data[filtered_data["Month"].isin(month)]

# ===== الرسوم البيانية =====

st.subheader("📅 Sales by Month")
sales_by_month = (
    filtered_data.groupby("Month")["TotalPrice"]
    .sum()
    .reset_index()
)

fig1 = px.line(sales_by_month, x="Month", y="TotalPrice")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("🌍 Sales by Country")
sales_by_country = (
    filtered_data.groupby("Country")["TotalPrice"]
    .sum()
    .reset_index()
    .sort_values(by="TotalPrice", ascending=False)
    .head(10)
)

fig2 = px.bar(sales_by_country, x="Country", y="TotalPrice")
st.plotly_chart(fig2, use_container_width=True)

st.subheader("🏷️ Top 10 Products by Revenue")
top_products = (
    filtered_data.groupby("Description")["TotalPrice"]
    .sum()
    .reset_index()
    .sort_values(by="TotalPrice", ascending=False)
    .head(10)
)

fig3 = px.bar(
    top_products,
    x="TotalPrice",
    y="Description",
    orientation="h"
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ===== عرض توصيات التسويق =====
st.subheader("📢 Marketing Strategy Recommendations")
st.dataframe(strategy)

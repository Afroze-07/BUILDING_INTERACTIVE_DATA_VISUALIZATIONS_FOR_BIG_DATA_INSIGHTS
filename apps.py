import streamlit as st
import pandas as pd
import plotly.express as px

# Add Custom CSS Styling
st.markdown("""
    <style>
        .main {
            background-color: #f4f7fc;
            padding: 20px;
            font-family: 'Helvetica', sans-serif;
        }
        .sidebar .sidebar-content {
            background-color: #34495E;
            color: white;
            border-radius: 10px;
        }
        .stButton>button {
            background-color: #1abc9c;
            color: white;
            font-weight: bold;
        }
        .stTextInput input {
            border-radius: 5px;
        }
        .css-1d391kg {
            background-color: #ecf0f1;
        }
    </style>
""", unsafe_allow_html=True)

# Title
st.title("🚗 Used Car Market Dashboard")

# 📂 **File Upload**
st.sidebar.header("📂 Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file (Make sure it's in the correct format)", type=["csv"])

if uploaded_file:
    # Load dataset
    df = pd.read_csv(uploaded_file)

    # Ensure consistent column names
    df.columns = df.columns.str.lower().str.strip()

    # 📅 **Fixing 'posteddate' Column**
    if "posteddate" in df.columns:
        df["posteddate"] = pd.to_datetime(df["posteddate"], format="%b-%y", errors="coerce")
    else:
        st.error("⚠️ 'posteddate' column is missing in the dataset!")

    # 📌 **Sidebar Filters**
    st.sidebar.header("🚀 Welcome to Our Dashboard! 🎉📊")
    st.sidebar.header("🔍 Filters")

    # Brand Filter
    brand_filter = st.sidebar.multiselect("Filter by Brand:", df["brand"].unique(), key="brand_chart")
    brand_df = df[df["brand"].isin(brand_filter)] if brand_filter else df

    # Owner Type Filter
    owner_filter = st.sidebar.multiselect("Filter by Owner Type:", df["owner"].unique(), key="owner_chart")
    owner_df = df[df["owner"].isin(owner_filter)] if owner_filter else df

    # Transmission Filter
    trans_filter = st.sidebar.multiselect("Filter by Transmission:", df["transmission"].unique(), key="trans_chart")
    fuel_filter = st.sidebar.multiselect("Filter by Fuel Type:", df["fueltype"].unique(), key="fuel_chart")

    # Kilometer & Year Filters
    if "kmdriven" in df.columns and "year" in df.columns:
        df["kmdriven"] = df["kmdriven"].astype(str).str.replace(r"[^\d]", "", regex=True)
        df["kmdriven"] = pd.to_numeric(df["kmdriven"], errors="coerce")
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["kmdriven", "year"])

        min_km, max_km = int(df["kmdriven"].min()), int(df["kmdriven"].max())
        min_year, max_year = int(df["year"].min()), int(df["year"].max())

        km_filter = st.sidebar.slider("Filter by Kilometers Driven:", min_km, max_km, (min_km, max_km), key="km_chart")
        year_filter = st.sidebar.slider("Filter by Year:", min_year, max_year, (min_year, max_year), key="year_chart")

    # Posted Month Filter
    if "posteddate" in df.columns:
        df["posted_month"] = df["posteddate"].dt.strftime("%Y-%m")
        month_filter = st.sidebar.multiselect("Filter by Month:", df["posted_month"].unique(), key="month_chart")

    # Apply filters
    df = df[df["brand"].isin(brand_filter)] if brand_filter else df
    df = df[df["owner"].isin(owner_filter)] if owner_filter else df
    df = df[df["transmission"].isin(trans_filter)] if trans_filter else df
    df = df[df["fueltype"].isin(fuel_filter)] if fuel_filter else df
    df = df[df["posted_month"].isin(month_filter)] if month_filter else df
    df = df[(df["kmdriven"] >= km_filter[0]) & (df["kmdriven"] <= km_filter[1])] if "kmdriven" in df.columns else df
    df = df[(df["year"] >= year_filter[0]) & (df["year"] <= year_filter[1])] if "year" in df.columns else df

    # Dynamic Title with Filter Counts
    st.title(f"🚗 Used Car Market Dashboard ({len(df)} records displayed)")

    # 📊 **Charts**
    st.subheader("📊 Car Brands Distribution")
    if not df.empty:
        fig_brand = px.bar(df, x="brand", title="Car Brands Count", color="brand")
        st.plotly_chart(fig_brand)

    st.subheader("👤 Owner Type Distribution")
    if not df.empty:
        fig_owner = px.pie(df, names="owner", title="Owner Type Percentage")
        st.plotly_chart(fig_owner)

    st.subheader("⚙️ Transmission vs. Fuel Type")
    if not df.empty:
        fig_trans_fuel = px.histogram(df, x="transmission", color="fueltype", barmode="group", title="Transmission vs. Fuel Type")
        st.plotly_chart(fig_trans_fuel)

    st.subheader("📏 Kilometers Driven Over Time")
    if not df.empty:
        df["kmdriven (in '000s)"] = df["kmdriven"] / 1000
        fig_km = px.scatter(df, x="year", y="kmdriven (in '000s)", title="Kilometers Driven Over Time", color="year")
        st.plotly_chart(fig_km)

    st.subheader("📅 Cars Listed Over Time")
    if not df.empty and "posted_month" in df.columns:
        fig_time = px.line(df.groupby("posted_month").size().reset_index(name="count"), x="posted_month", y="count", title="Car Listings Over Time")
        st.plotly_chart(fig_time)

    st.subheader("💰 Asking Price by Fuel Type")
    if not df.empty:
        fig_fuel_price = px.box(df, x="fueltype", y="askprice", color="fueltype", title="Fuel Type vs. Asking Price")
        st.plotly_chart(fig_fuel_price)

    st.subheader("⚙️ Transmission Type vs. Kilometers Driven")
    if not df.empty:
        fig_trans_km = px.scatter(df, x="transmission", y="kmdriven", color="transmission", title="Transmission Type vs. Kilometers Driven")
        st.plotly_chart(fig_trans_km)

    st.subheader("👤 Owner Type vs. Asking Price")
    if not df.empty:
        fig_owner_price = px.bar(df, x="owner", y="askprice", color="owner", title="Owner Type vs. Asking Price")
        st.plotly_chart(fig_owner_price)

    # 📜 **Filtered Data Table**
    st.subheader("📜 Filtered Data")
    st.write(df)

else:
    st.warning("⚠️ Please upload a CSV file to proceed!")

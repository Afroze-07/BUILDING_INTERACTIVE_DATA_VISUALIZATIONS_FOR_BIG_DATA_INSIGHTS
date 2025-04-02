import streamlit as st
import pandas as pd
import plotly.express as px

# Title
st.title("🚗 Used Car Market Dashboard")

# 📌 **File Upload**
st.sidebar.header("📂 Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    # Load dataset
    df = pd.read_csv(uploaded_file)

    # Ensure consistent column names
    df.columns = df.columns.str.lower().str.strip()

    # Fixing posteddate column
    if "posteddate" in df.columns:
        df["posteddate"] = pd.to_datetime(df["posteddate"], format="%b-%y", errors="coerce")
    else:
        st.error("⚠️ 'posteddate' column is missing in the dataset!")

    # 📌 **Sidebar Filters**
    st.sidebar.header("🔍 Filters")

    # Brand Filter
    if "brand" in df.columns:
        brand_filter = st.sidebar.multiselect("Filter by Brand:", df["brand"].unique(), key="brand_chart")
        df = df[df["brand"].isin(brand_filter)] if brand_filter else df

    # Owner Type Filter
    if "owner" in df.columns:
        owner_filter = st.sidebar.multiselect("Filter by Owner Type:", df["owner"].unique(), key="owner_chart")
        df = df[df["owner"].isin(owner_filter)] if owner_filter else df

    # Transmission Filter
    if "transmission" in df.columns:
        trans_filter = st.sidebar.multiselect("Filter by Transmission:", df["transmission"].unique(), key="trans_chart")
        df = df[df["transmission"].isin(trans_filter)] if trans_filter else df

    # Fuel Type Filter
    if "fueltype" in df.columns:
        fuel_filter = st.sidebar.multiselect("Filter by Fuel Type:", df["fueltype"].unique(), key="fuel_chart")
        df = df[df["fueltype"].isin(fuel_filter)] if fuel_filter else df

    # Kilometer & Year Filters
    if "kmdriven" in df.columns and "year" in df.columns:
        df["kmdriven"] = pd.to_numeric(df["kmdriven"], errors="coerce")
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["kmdriven", "year"])

        min_km, max_km = int(df["kmdriven"].min()), int(df["kmdriven"].max())
        min_year, max_year = int(df["year"].min()), int(df["year"].max())

        km_filter = st.sidebar.slider("Kilometers Driven:", min_km, max_km, (min_km, max_km), key="km_chart")
        year_filter = st.sidebar.slider("Year:", min_year, max_year, (min_year, max_year), key="year_chart")

        df = df[(df["kmdriven"] >= km_filter[0]) & (df["kmdriven"] <= km_filter[1])]
        df = df[(df["year"] >= year_filter[0]) & (df["year"] <= year_filter[1])]

    # 📊 **Charts**
    if not df.empty:
        st.subheader("📊 Car Brands Distribution")
        fig_brand = px.bar(df, x="brand", title="Car Brands Count", color="brand")
        st.plotly_chart(fig_brand)

        st.subheader("👤 Owner Type Distribution")
        fig_owner = px.pie(df, names="owner", title="Owner Type Percentage")
        st.plotly_chart(fig_owner)

        st.subheader("⚙️ Transmission vs. Fuel Type")
        fig_trans_fuel = px.histogram(df, x="transmission", color="fueltype", barmode="group", title="Transmission vs. Fuel Type")
        st.plotly_chart(fig_trans_fuel)

        st.subheader("📏 Kilometers Driven Over Time")
        df["kmdriven (in '000s)"] = df["kmdriven"] / 1000
        fig_km = px.scatter(df, x="year", y="kmdriven (in '000s)", title="Kilometers Driven Over Time", color="year")
        st.plotly_chart(fig_km)

        st.subheader("📅 Cars Listed Over Time")
        if "posteddate" in df.columns:
            df["posted_month"] = df["posteddate"].dt.strftime("%Y-%m")
            fig_time = px.line(df.groupby("posted_month").size().reset_index(name="count"), x="posted_month", y="count", title="Car Listings Over Time")
            st.plotly_chart(fig_time)

        st.subheader("💰 Asking Price by Fuel Type")
        if "askprice" in df.columns:
            fig_fuel_price = px.box(df, x="fueltype", y="askprice", color="fueltype", title="Fuel Type vs. Asking Price")
            st.plotly_chart(fig_fuel_price)

    # 📜 **Filtered Data Table**
    st.subheader("📜 Filtered Data")
    st.write(df)

else:
    st.warning("⚠️ Please upload a CSV file to proceed!")

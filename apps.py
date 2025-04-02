import streamlit as st
import pandas as pd
import plotly.express as px

# 🚗 **Used Car Market Dashboard**
st.title("🚗 Used Car Market Dashboard")

# 📂 **File Upload**
st.sidebar.header("📂 Upload Your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file:
    # Load dataset
    df = pd.read_csv(uploaded_file)

    # Ensure consistent column names
    df.columns = df.columns.str.lower().str.strip()

    # 📅 **Fixing 'posteddate' Column**
    if "posteddate" in df.columns:
        df["posteddate"] = pd.to_datetime(df["posteddate"], format="%b-%y", errors="coerce")
        df["posted_month"] = df["posteddate"].dt.strftime("%Y-%m")  # Extract Month-Year
    else:
        st.error("⚠️ 'posteddate' column is missing in the dataset!")

    # 🔍 **Sidebar Filters**
    st.sidebar.header("🔍 Filters")

    # 🏷 **Brand Filter**
    if "brand" in df.columns:
        brand_filter = st.sidebar.multiselect("Filter by Brand:", df["brand"].unique(), key="brand_chart")
        df = df[df["brand"].isin(brand_filter)] if brand_filter else df

    # 👤 **Owner Type Filter**
    if "owner" in df.columns:
        owner_filter = st.sidebar.multiselect("Filter by Owner Type:", df["owner"].unique(), key="owner_chart")
        df = df[df["owner"].isin(owner_filter)] if owner_filter else df

    # ⚙️ **Transmission Filter**
    if "transmission" in df.columns:
        trans_filter = st.sidebar.multiselect("Filter by Transmission:", df["transmission"].unique(), key="trans_chart")
        df = df[df["transmission"].isin(trans_filter)] if trans_filter else df

    # ⛽ **Fuel Type Filter**
    if "fueltype" in df.columns:
        fuel_filter = st.sidebar.multiselect("Filter by Fuel Type:", df["fueltype"].unique(), key="fuel_chart")
        df = df[df["fueltype"].isin(fuel_filter)] if fuel_filter else df

    # 📏 **Kilometer & Year Filters**
    if "kmdriven" in df.columns and "year" in df.columns:
        df["kmdriven"] = pd.to_numeric(df["kmdriven"], errors="coerce")  # Convert to numeric
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df.dropna(subset=["kmdriven", "year"])  # Remove NaN values

        # Set min/max for filters
        if not df.empty:
            min_km, max_km = int(df["kmdriven"].min()), int(df["kmdriven"].max())
            min_year, max_year = int(df["year"].min()), int(df["year"].max())
        else:
            min_km, max_km = 0, 100000  # Default values
            min_year, max_year = 2000, 2025

        # Add sidebar sliders
        km_filter = st.sidebar.slider("Kilometers Driven:", min_km, max_km, (min_km, max_km), key="km_chart")
        year_filter = st.sidebar.slider("Year:", min_year, max_year, (min_year, max_year), key="year_chart")

        # Apply filters
        df = df[(df["kmdriven"] >= km_filter[0]) & (df["kmdriven"] <= km_filter[1])]
        df = df[(df["year"] >= year_filter[0]) & (df["year"] <= year_filter[1])]

    # 💰 **Price Filter**
    if "askprice" in df.columns:
        df["askprice"] = pd.to_numeric(df["askprice"], errors="coerce")  # Convert to numeric
        df = df.dropna(subset=["askprice"])  # Remove NaN values

        # Set min/max for price filter
        if not df.empty:
            min_price, max_price = int(df["askprice"].min()), int(df["askprice"].max())
        else:
            min_price, max_price = 0, 1000000  # Default fallback values

        # Add price slider
        price_filter = st.sidebar.slider("Filter by Asking Price:", min_price, max_price, (min_price, max_price))
        df = df[(df["askprice"] >= price_filter[0]) & (df["askprice"] <= price_filter[1])]

    # 📊 **Visualizations**
    if not df.empty:
        # 📊 Car Brand Distribution
        st.subheader("📊 Car Brands Distribution")
        fig_brand = px.bar(df, x="brand", title="Car Brands Count", color="brand")
        st.plotly_chart(fig_brand)

        # 👤 Owner Type Distribution
        st.subheader("👤 Owner Type Distribution")
        fig_owner = px.pie(df, names="owner", title="Owner Type Percentage")
        st.plotly_chart(fig_owner)

        # ⚙️ Transmission vs. Fuel Type
        st.subheader("⚙️ Transmission vs. Fuel Type")
        fig_trans_fuel = px.histogram(df, x="transmission", color="fueltype", barmode="group", title="Transmission vs. Fuel Type")
        st.plotly_chart(fig_trans_fuel)

        # 📏 Kilometers Driven Over Time
        st.subheader("📏 Kilometers Driven Over Time")
        df["kmdriven (in '000s)"] = df["kmdriven"] / 1000  # Convert to thousands
        fig_km = px.scatter(df, x="year", y="kmdriven (in '000s)", title="Kilometers Driven Over Time", color="year")
        st.plotly_chart(fig_km)

        # 📅 Cars Listed Over Time
        if "posted_month" in df.columns:
            st.subheader("📅 Cars Listed Over Time")
            fig_time = px.line(df.groupby("posted_month").size().reset_index(name="count"), x="posted_month", y="count", title="Car Listings Over Time")
            st.plotly_chart(fig_time)

        # 💰 Asking Price by Fuel Type
        if "askprice" in df.columns:
            st.subheader("💰 Asking Price by Fuel Type")
            fig_fuel_price = px.box(df, x="fueltype", y="askprice", color="fueltype", title="Fuel Type vs. Asking Price")
            st.plotly_chart(fig_fuel_price)

    # 📜 **Filtered Data Table**
    st.subheader("📜 Filtered Data")
    st.write(df)

else:
    st.warning("⚠️ Please upload a CSV file to proceed!")

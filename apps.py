import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
file_path = "used_car_dataset.csv"  # Ensure correct path
df = pd.read_csv(file_path)

# Ensure consistent column names
df.columns = df.columns.str.lower().str.strip()

# Fixing posteddate column
if "posteddate" in df.columns:
    df["posteddate"] = pd.to_datetime(df["posteddate"], format="%b-%y", errors="coerce")
else:
    st.error("⚠️ 'posteddate' column is missing in the dataset!")

# 🏁 **Welcome Section**
st.title("🚗 Used Car Market Dashboard")

# 📌 **Sidebar Filters**
st.sidebar.header("** 📢Welcome to the Ultimate Used Car Market Insights Dashboard!**")
st.sidebar.header("🎛️ Customize Your Search")
# 🚗 **Brand Filter**
st.sidebar.markdown("🔹 **Select car brands you want to explore**")
brand_filter = st.sidebar.multiselect("Choose Brand(s):", df["brand"].unique(), key="brand_chart")
brand_df = df[df["brand"].isin(brand_filter)] if brand_filter else df

# 👤 **Owner Type Filter**
st.sidebar.markdown("🔹 **Filter cars by the number of previous owners**")
owner_filter = st.sidebar.multiselect("Choose Owner Type(s):", df["owner"].unique(), key="owner_chart")
owner_df = df[df["owner"].isin(owner_filter)] if owner_filter else df

# ⚙️ **Transmission Filter**
st.sidebar.markdown("🔹 **Choose Manual or Automatic Transmission**")
trans_filter = st.sidebar.multiselect("Choose Transmission Type(s):", df["transmission"].unique(), key="trans_chart")

# ⛽ **Fuel Type Filter**
st.sidebar.markdown("🔹 **Select fuel type (Petrol, Diesel, CNG, etc.)**")
fuel_filter = st.sidebar.multiselect("Choose Fuel Type(s):", df["fueltype"].unique(), key="fuel_chart")

# 🛣️ **Kilometers Driven & Year Filters**
if "kmdriven" in df.columns and "year" in df.columns:
    df["kmdriven"] = df["kmdriven"].astype(str).str.replace(r"[^\d]", "", regex=True)
    df["kmdriven"] = pd.to_numeric(df["kmdriven"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df = df.dropna(subset=["kmdriven", "year"])

    min_km, max_km = int(df["kmdriven"].min()), int(df["kmdriven"].max())
    min_year, max_year = int(df["year"].min()), int(df["year"].max())

    st.sidebar.markdown("🔹 **Refine results by kilometers driven & car age**")
    km_filter = st.sidebar.slider("Kilometers Driven:", min_km, max_km, (min_km, max_km), key="km_chart")
    year_filter = st.sidebar.slider("Car Year:", min_year, max_year, (min_year, max_year), key="year_chart")

# 📅 **Posted Month Filter**
if "posteddate" in df.columns:
    df["posted_month"] = df["posteddate"].dt.strftime("%Y-%m")
    st.sidebar.markdown("🔹 **View cars listed in specific months**")
    month_filter = st.sidebar.multiselect("Choose Listing Month(s):", df["posted_month"].unique(), key="month_chart")

# Apply filters
df = df[df["brand"].isin(brand_filter)] if brand_filter else df
df = df[df["owner"].isin(owner_filter)] if owner_filter else df
df = df[df["transmission"].isin(trans_filter)] if trans_filter else df
df = df[df["fueltype"].isin(fuel_filter)] if fuel_filter else df
df = df[df["posted_month"].isin(month_filter)] if month_filter else df
df = df[(df["kmdriven"] >= km_filter[0]) & (df["kmdriven"] <= km_filter[1])] if "kmdriven" in df.columns else df
df = df[(df["year"] >= year_filter[0]) & (df["year"] <= year_filter[1])] if "year" in df.columns else df

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
st.subheader("📜 Explore Your Filtered Dataset")
if not df.empty:
    st.write(df)
else:
    st.warning("⚠️ No matching data found! Try adjusting your filters.")

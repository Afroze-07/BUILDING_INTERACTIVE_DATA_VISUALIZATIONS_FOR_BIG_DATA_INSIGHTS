import streamlit as st
import pandas as pd
import plotly.express as px
import base64
from fpdf import FPDF

# --- Page Setup ---
st.set_page_config(page_title="Used Car Insights", layout="wide")

# --- Theme Setup ---
st.sidebar.title("🧑‍🎨 Appearance Settings")
theme = st.sidebar.radio("🎨 Select Theme", ["☀️ Light", "🌙 Dark"], index=0)

def set_theme(theme_choice):
    if "Dark" in theme_choice:
        st.session_state["theme_mode"] = "dark"
        custom_css = """
        <style>
        body {
            background-color: #121212;
            color: white;
        }
        .reportview-container, .main, .block-container {
            background-color: #121212;
            color: white;
        }
        table, th, td {
            color: white !important;
        }
        .stDataFrame div {
            color: white !important;
        }
        </style>
        """
    else:
        st.session_state["theme_mode"] = "light"
        custom_css = """
        <style>
        body {
            background-color: white;
            color: black;
        }
        .reportview-container, .main, .block-container {
            background-color: white;
            color: black;
        }
        table, th, td {
            color: black !important;
        }
        .stDataFrame div {
            color: black !important;
        }
        </style>
        """
    st.markdown(custom_css, unsafe_allow_html=True)

set_theme(theme)

# --- Branding ---
st.markdown("""
    <div style='text-align: center; padding: 20px 0;'>
        <h1 style='font-size: 3em; color:white; font-family: "Segoe UI", sans-serif;'>
            🚘 Smart Used Car Explorer
        </h1>
        <p style='font-size: 1.25em; color: white;'>Explore, Compare, and Decide Smarter 🚀</p>
        <hr style='height: 4px; border: none; background-color: #D6DBDF; border-radius: 2px;'>
    </div>
""", unsafe_allow_html=True)

# --- File Upload ---
uploaded_file = st.file_uploader("📁 Upload Your Cleaned Used Car CSV File", type=["csv"])

# --- Suggestion Function ---
def suggest_car(filtered_df):
    valid_df = filtered_df.copy()
    valid_df = valid_df[valid_df["kmdriven"].notna()]
    valid_df = valid_df[valid_df["kmdriven"] > 1000]

    if valid_df.empty:
        return "❌ Sorry, no suggestions available. Please adjust your filters."

    budget_limit = valid_df["askprice"].quantile(0.25)
    smart_choices = valid_df[valid_df["askprice"] <= budget_limit].sort_values(by="kmdriven").head(1)

    if smart_choices.empty:
        return "⚠️ No smart picks found under your current budget and preferences."

    row = smart_choices.iloc[0]
    return f"We recommend the **{row['brand']} {row['model']} ({int(row['year'])})** – {int(row['kmdriven'])} KM driven, priced at ₹{int(row['askprice'])}."

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

    required_columns = ['brand', 'model', 'year', 'askprice', 'fueltype', 'transmission', 'owner', 'kmdriven']
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"⚠️ Missing required columns: {missing_cols}")
        st.stop()

    df["askprice"] = df["askprice"].astype(str).str.replace(r"[^0-9]", "", regex=True)
    df["askprice"] = pd.to_numeric(df["askprice"], errors="coerce")
    df["askprice"].fillna(df["askprice"].median(), inplace=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # Sidebar Filters
    st.sidebar.title("🔍 Find the Best Car for You")
    budget = st.sidebar.number_input("💰 Your Budget", 10000, 5000000, step=5000, value=300000)
    selected_fuel = st.sidebar.selectbox("⛽ Fuel Type", ["All"] + df["fueltype"].dropna().unique().tolist())
    selected_trans = st.sidebar.selectbox("⚙️ Transmission", ["All"] + df["transmission"].dropna().unique().tolist())
    selected_owner = st.sidebar.selectbox("👤 Owner", ["All"] + df["owner"].dropna().unique().tolist())
    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    year_range = st.sidebar.slider("📅 Year Range", min_year, max_year, (min_year, max_year))
    sort_option = st.sidebar.selectbox("📊 Sort By", ["askprice", "kmdriven", "year"])
    unit_toggle = st.sidebar.radio("💲 Price Unit", ["INR", "Lakh"])
    price_divisor = 100000 if unit_toggle == "Lakh" else 1

    # Filter Application
    filtered = df.copy()
    filtered = filtered[filtered["askprice"] <= budget]
    if selected_fuel != "All":
        filtered = filtered[filtered["fueltype"] == selected_fuel]
    if selected_trans != "All":
        filtered = filtered[filtered["transmission"] == selected_trans]
    if selected_owner != "All":
        filtered = filtered[filtered["owner"] == selected_owner]
    filtered = filtered[(filtered["year"] >= year_range[0]) & (filtered["year"] <= year_range[1])]
    filtered["displayprice"] = filtered["askprice"] / price_divisor

    if not filtered.empty:
        st.subheader("📊 Car Price Visualizations")
        chart_type = st.selectbox("📈 Choose Chart Type", ["Bar Chart", "Pie Chart", "Scatter Plot"])
        if chart_type == "Bar Chart":
            fig = px.bar(filtered, x="brand", y="displayprice", color="brand", title="Car Prices by Brand", labels={"displayprice": f"Price ({unit_toggle})"})
        elif chart_type == "Pie Chart":
            fig = px.pie(filtered, names="brand", title="Car Brand Distribution")
        elif chart_type == "Scatter Plot":
            fig = px.scatter(filtered, x="kmdriven", y="displayprice", color="brand", title="KM Driven vs Price", labels={"displayprice": f"Price ({unit_toggle})"})
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Filtered Car Results")
        st.dataframe(filtered[["brand", "model", "year", "askprice", "fueltype", "transmission", "owner"]])

        st.markdown("### 🌟 Top 3 Picks")
        top3 = filtered.sort_values(by=sort_option).head(3)
        for _, row in top3.iterrows():
            price_display = f"{int(row['askprice']/price_divisor)} {unit_toggle}" if unit_toggle == "Lakh" else f"₹{int(row['askprice'])}"
            st.markdown(f"""
                <div style='border:1px solid #444; padding:10px; border-radius:10px; margin-bottom:10px;'>
                    <b>✅ {row['brand']} {row['model']} ({int(row['year'])})</b><br>
                    Price: {price_display} | KM Driven: {int(row['kmdriven'])} | Fuel: {row['fueltype']} | Transmission: {row['transmission']}
                </div>
            """, unsafe_allow_html=True)

        st.success("🌟 These cars are great picks within your budget!")

        # Download
        csv = filtered.to_csv(index=False)
        st.download_button("⬇️ Download Filtered Results", csv, file_name="filtered_cars.csv", mime="text/csv")

        # PDF Report
        def create_pdf(data):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Used Car Filtered Report", ln=True, align="C")
            for _, row in data.iterrows():
                line = f"{row['brand']} {row['model']} - INR {int(row['askprice'])}"
                pdf.cell(200, 10, txt=line, ln=True)
            return pdf.output(dest="S").encode("latin1")

        if st.button("📄 Export to PDF"):
            pdf_bytes = create_pdf(top3)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Top3_Cars_Report.pdf">📄 Click to Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

        # Brand Summary
        st.subheader("📊 Brand-wise Average Price")
        brand_avg = filtered.groupby("brand")["askprice"].mean().reset_index()
        brand_avg["askprice"] = (brand_avg["askprice"] / price_divisor).round(2)
        brand_avg.columns = ["Brand", f"Avg Price ({unit_toggle})"]
        st.dataframe(brand_avg)

        # AI Suggestion
        st.markdown("### 🤖 Smart Suggestion!")
        ai_suggestion = suggest_car(filtered)
        st.info(ai_suggestion)

    else:
        st.warning("⚠️ No cars match your filters.")
else:
    st.info("📂 Please upload a CSV file to continue.")
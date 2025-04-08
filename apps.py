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
    <style>
        .custom-title {
            text-align: center;
            color: white !important;
            font-size: 48px;
            font-weight: bold;
        }
        .custom-line {
            border-top: 3px solid white !important;
            margin-top: 10px;
            margin-bottom: 30px;
        }
    </style>
    <h1 class="custom-title">🚗 Used Car Insights Dashboard</h1>
    <hr class="custom-line">
""", unsafe_allow_html=True)



# --- Upload File ---
uploaded_file = st.file_uploader("📁 Upload Your Cleaned Used Car CSV File", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Normalize column names
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "")

    required_columns = ['brand', 'model', 'year', 'askprice', 'fueltype', 'transmission', 'owner', 'kmdriven']
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"⚠️ The following required columns are missing in your CSV: {missing_cols}")
        st.stop()

    df["askprice"] = df["askprice"].astype(str).str.replace(r"[^0-9]", "", regex=True)
    df["askprice"] = pd.to_numeric(df["askprice"], errors="coerce")
    df["askprice"].fillna(df["askprice"].median(), inplace=True)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")

    # --- Sidebar Filters ---
    st.sidebar.title("🔍 Find the Best Car for You")
    budget = st.sidebar.number_input("💰 Your Budget", 10000, 5000000, step=5000, value=300000)

    fuel_types = df["fueltype"].dropna().unique().tolist()
    selected_fuel = st.sidebar.selectbox("⛽ Fuel Type", ["All"] + fuel_types)

    transmissions = df["transmission"].dropna().unique().tolist()
    selected_trans = st.sidebar.selectbox("⚙️ Transmission", ["All"] + transmissions)

    owners = df["owner"].dropna().unique().tolist()
    selected_owner = st.sidebar.selectbox("👤 Owner", ["All"] + owners)

    min_year, max_year = int(df["year"].min()), int(df["year"].max())
    year_range = st.sidebar.slider("📅 Year Range", min_year, max_year, (min_year, max_year))

    sort_option = st.sidebar.selectbox("📊 Sort By", ["askprice", "kmdriven", "year"])
    unit_toggle = st.sidebar.radio("💲 Price Unit", ["INR", "Lakh"])
    price_divisor = 100000 if unit_toggle == "Lakh" else 1

    # --- Apply Filters ---
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
        # --- Charts ---
        st.subheader("📊 Car Price Visualizations")
        chart_type = st.selectbox("📈 Choose Chart Type", ["Bar Chart", "Pie Chart", "Scatter Plot"])
        if chart_type == "Bar Chart":
            fig = px.bar(filtered, x="brand", y="displayprice", color="brand", title="Car Prices by Brand", labels={"displayprice": f"Price ({unit_toggle})"})
        elif chart_type == "Pie Chart":
            fig = px.pie(filtered, names="brand", title="Car Brand Distribution")
        elif chart_type == "Scatter Plot":
            fig = px.scatter(filtered, x="kmdriven", y="displayprice", color="brand", title="KM Driven vs Price", labels={"displayprice": f"Price ({unit_toggle})"})
        st.plotly_chart(fig, use_container_width=True)

        # --- Filtered Data ---
        st.subheader("📋 Filtered Car Results")
        st.dataframe(filtered[["brand", "model", "year", "askprice", "fueltype", "transmission", "owner"]])

        # --- Top 3 Picks ---
        st.markdown("### 🌟 Top 3 Picks")
        top3 = filtered.sort_values(by=sort_option).head(3)

        st.markdown("""
            <style>
            .top-pick-card {
                display: flex;
                align-items: center;
                border: 1px solid #444;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                transition: all 0.3s ease;
                background: transparent;
            }
            .top-pick-card:hover {
                box-shadow: 0 0 15px rgba(0,0,0,0.3);
                transform: scale(1.02);
            }
            .top-pick-text {
                color: inherit;
            }
            .top-pick-heading {
                margin: 0;
                font-size: 20px;
                font-weight: bold;
            }
            .top-pick-sub {
                margin: 0;
                font-size: 14px;
                opacity: 0.8;
            }
            </style>
        """, unsafe_allow_html=True)

        for _, row in top3.iterrows():
            price_display = f"{int(row['askprice']/price_divisor)} {unit_toggle}" if unit_toggle == "Lakh" else f"₹{int(row['askprice'])}"
            st.markdown(f"""
                <div class="top-pick-card">
                    <div class="top-pick-text">
                        <p class="top-pick-heading">✅ {row['brand']} {row['model']} ({int(row['year'])}) – {price_display}</p>
                        <p class="top-pick-sub">KM Driven: {int(row['kmdriven'])} | Fuel: {row['fueltype']} | Transmission: {row['transmission']}</p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        st.success("🎯 These cars are great picks within your budget!")

        # --- Download CSV ---
        csv = filtered.to_csv(index=False)
        st.download_button("⬇️ Download Filtered Results", csv, file_name="filtered_cars.csv", mime="text/csv")

        # --- Export PDF Report ---
        st.markdown("### 📄 Export PDF Report")
        def create_pdf(data):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Used Car Filtered Report", ln=True, align="C")
            for _, row in data.iterrows():
                price_text = f"{row['brand']} {row['model']} - INR {int(row['askprice'])}"
                pdf.cell(200, 10, txt=price_text, ln=True)
            return pdf.output(dest="S").encode("latin1")

        if st.button("📤 Export to PDF"):
            pdf_bytes = create_pdf(top3)
            b64 = base64.b64encode(pdf_bytes).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Top3_Cars_Report.pdf">📄 Click to Download PDF</a>'
            st.markdown(href, unsafe_allow_html=True)

        # --- Brand-wise Summary ---
        st.subheader("📊 Brand-wise Average Price")
        brand_avg = filtered.groupby("brand")["askprice"].mean().reset_index()
        brand_avg["askprice"] = (brand_avg["askprice"] / price_divisor).round(2)
        brand_avg.columns = ["Brand", f"Avg Price ({unit_toggle})"]
        st.dataframe(brand_avg)
    else:
        st.warning("⚠️ No cars match your filters.")
else:
    st.info("📂 Please upload a CSV file to continue.")

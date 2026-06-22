import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Baucar CIDB", layout="wide")

CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?output=csv"

@st.cache_data(ttl=300)
def load_data():
    df = pd.read_csv(CSV_URL)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("Dashboard Keluar Masuk Baucar CIDB")

df["BULAN/TAHUN"] = df["BULAN/TAHUN"].astype(str)
df["BULAN"] = df["BULAN/TAHUN"].str.extract(r"([A-Za-z]+)")
df["TAHUN"] = df["BULAN/TAHUN"].str.extract(r"(\d{4})")

st.sidebar.header("Filter")

tahun = st.sidebar.multiselect(
    "Tahun",
    sorted(df["TAHUN"].dropna().unique()),
    default=sorted(df["TAHUN"].dropna().unique())
)

bulan = st.sidebar.multiselect(
    "Bulan",
    sorted(df["BULAN"].dropna().unique()),
    default=sorted(df["BULAN"].dropna().unique())
)

df_filter = df[
    df["TAHUN"].isin(tahun) &
    df["BULAN"].isin(bulan)
]

if "Name" in df.columns:
    carian = st.sidebar.text_input("Cari Nama")
    if carian:
        df_filter = df_filter[
            df_filter["Name"].astype(str).str.contains(carian, case=False, na=False)
        ]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Baucar 2024", len(df_filter[df_filter["TAHUN"] == "2024"]))
col2.metric("Baucar 2025", len(df_filter[df_filter["TAHUN"] == "2025"]))
col3.metric("Baucar 2026", len(df_filter[df_filter["TAHUN"] == "2026"]))
col4.metric("Total Baucar", len(df_filter))

st.divider()

if "ID" in df_filter.columns:
    chart_id = (
        df_filter.groupby("ID")
        .size()
        .reset_index(name="Jumlah")
        .sort_values("Jumlah", ascending=False)
    )

    fig = px.bar(
        chart_id,
        x="ID",
        y="Jumlah",
        text="Jumlah",
        title="Jumlah Baucar Mengikut ID"
    )

    st.plotly_chart(fig, use_container_width=True)

st.subheader("Senarai Baucar")
st.dataframe(df_filter, use_container_width=True)

csv = df_filter.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Data CSV",
    csv,
    "data_baucar_cidb.csv",
    "text/csv"
)
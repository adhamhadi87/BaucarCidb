import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Baucar CIDB",
    layout="wide"
)

BAUCAR_CSV_URL = "https://docs.google.com/spreadsheets/d/1UmIsdnsz46lcPdLIEhTjry6E-ZOrNS3YDXKIqkxZV1s/export?format=csv&gid=1370653594"
DATA_APP_CSV_URL = "https://docs.google.com/spreadsheets/d/1UmIsdnsz46lcPdLIEhTjry6E-ZOrNS3YDXKIqkxZV1s/export?format=csv&gid=1657707039"


@st.cache_data(ttl=300)
def load_csv(url):
    df = pd.read_csv(url)
    df.columns = df.columns.astype(str).str.strip()
    return df


def clean_no_baucar(series):
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", "", regex=True)
    )


baucar = load_csv(BAUCAR_CSV_URL)
data_app = load_csv(DATA_APP_CSV_URL)

st.title("Dashboard Keluar Masuk Baucar CIDB")

baucar = baucar.rename(columns={
    "BULAN/TAHUN": "BULAN_TAHUN",
    "NO BAUCAR": "NO_BAUCAR",
    "Name": "NAMA",
    "ID": "ID"
})

data_app = data_app.rename(columns={
    "DATE": "DATE",
    "IN/OUT": "IN_OUT",
    "BULAN /TAHUN": "BULAN_TAHUN",
    "BULAN/TAHUN": "BULAN_TAHUN",
    "NO. BAUCAR": "NO_BAUCAR",
    "NO BAUCAR": "NO_BAUCAR",
    "NO KOTAK": "NO_KOTAK",
    "KOTAK TAMBAHAN": "KOTAK_TAMBAHAN",
    "EMAIL": "EMAIL"
})

required_baucar = ["NO_BAUCAR", "NAMA", "ID"]
required_data_app = ["NO_BAUCAR", "IN_OUT", "BULAN_TAHUN"]

missing_baucar = [c for c in required_baucar if c not in baucar.columns]
missing_data_app = [c for c in required_data_app if c not in data_app.columns]

if missing_baucar:
    st.error(f"Column tidak dijumpai dalam sheet BAUCAR: {missing_baucar}")
    st.write("Column BAUCAR yang dibaca:", list(baucar.columns))
    st.stop()

if missing_data_app:
    st.error(f"Column tidak dijumpai dalam sheet DATA APP: {missing_data_app}")
    st.write("Column DATA APP yang dibaca:", list(data_app.columns))
    st.stop()

baucar["NO_BAUCAR"] = clean_no_baucar(baucar["NO_BAUCAR"])
data_app["NO_BAUCAR"] = clean_no_baucar(data_app["NO_BAUCAR"])

df = data_app.merge(
    baucar[["NO_BAUCAR", "NAMA", "ID"]],
    on="NO_BAUCAR",
    how="left"
)

df["BULAN_TAHUN"] = df["BULAN_TAHUN"].astype(str)
df["TAHUN"] = df["BULAN_TAHUN"].str.extract(r"(\d{4})")
df["BULAN"] = df["BULAN_TAHUN"].str.extract(r"([A-Za-zÀ-ÿ]+)")

if "DATE" in df.columns:
    df["DATE"] = pd.to_datetime(df["DATE"], errors="coerce", dayfirst=True)

st.sidebar.header("Filter")

tahun_list = sorted(df["TAHUN"].dropna().unique())
tahun = st.sidebar.multiselect("Tahun", tahun_list, default=tahun_list)

bulan_list = sorted(df["BULAN"].dropna().unique())
bulan = st.sidebar.multiselect("Bulan", bulan_list, default=bulan_list)

status_list = sorted(df["IN_OUT"].dropna().astype(str).unique())
status = st.sidebar.multiselect("IN / OUT", status_list, default=status_list)

id_list = sorted(df["ID"].dropna().astype(str).unique())
id_filter = st.sidebar.multiselect("ID", id_list, default=id_list)

carian = st.sidebar.text_input("Cari Nama / No Baucar / Email / Kotak")

df_filter = df[
    df["TAHUN"].isin(tahun)
    & df["BULAN"].isin(bulan)
    & df["IN_OUT"].astype(str).isin(status)
    & df["ID"].astype(str).isin(id_filter)
]

if carian:
    df_filter = df_filter[
        df_filter.astype(str).apply(
            lambda row: row.str.contains(carian, case=False, na=False).any(),
            axis=1
        )
    ]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Pergerakan", len(df_filter))
col2.metric("Total Baucar Unik", df_filter["NO_BAUCAR"].nunique())
col3.metric("Total IN", len(df_filter[df_filter["IN_OUT"].astype(str).str.upper() == "IN"]))
col4.metric("Total OUT", len(df_filter[df_filter["IN_OUT"].astype(str).str.upper() == "OUT"]))

col5, col6, col7 = st.columns(3)
col5.metric("Baucar 2024", len(df_filter[df_filter["TAHUN"] == "2024"]))
col6.metric("Baucar 2025", len(df_filter[df_filter["TAHUN"] == "2025"]))
col7.metric("Baucar 2026", len(df_filter[df_filter["TAHUN"] == "2026"]))

st.divider()

c1, c2 = st.columns(2)

with c1:
    chart_status = (
        df_filter.groupby("IN_OUT")
        .size()
        .reset_index(name="Jumlah")
    )
    fig_status = px.pie(
        chart_status,
        names="IN_OUT",
        values="Jumlah",
        title="Pergerakan Baucar IN vs OUT",
        hole=0.4
    )
    st.plotly_chart(fig_status, use_container_width=True)

with c2:
    chart_id = (
        df_filter.groupby("ID")
        .size()
        .reset_index(name="Jumlah")
        .sort_values("Jumlah", ascending=False)
    )
    fig_id = px.bar(
        chart_id,
        x="ID",
        y="Jumlah",
        text="Jumlah",
        title="Jumlah Pergerakan Mengikut ID"
    )
    st.plotly_chart(fig_id, use_container_width=True)

chart_bulan = (
    df_filter.groupby(["TAHUN", "BULAN"])
    .size()
    .reset_index(name="Jumlah")
)

fig_bulan = px.bar(
    chart_bulan,
    x="BULAN",
    y="Jumlah",
    color="TAHUN",
    barmode="group",
    text="Jumlah",
    title="Trend Pergerakan Baucar Mengikut Bulan"
)

st.plotly_chart(fig_bulan, use_container_width=True)

st.subheader("Top 20 Nama / Penerima")

top_nama = (
    df_filter.groupby("NAMA")
    .size()
    .reset_index(name="Jumlah")
    .sort_values("Jumlah", ascending=False)
    .head(20)
)

fig_nama = px.bar(
    top_nama,
    x="Jumlah",
    y="NAMA",
    orientation="h",
    text="Jumlah",
    title="Top 20 Nama Mengikut Pergerakan Baucar"
)

st.plotly_chart(fig_nama, use_container_width=True)

st.subheader("Senarai Perjalanan Baucar")

papar_cols = [
    "DATE",
    "IN_OUT",
    "BULAN_TAHUN",
    "NO_BAUCAR",
    "NAMA",
    "ID",
    "NO_KOTAK",
    "KOTAK_TAMBAHAN",
    "EMAIL"
]

papar_cols = [col for col in papar_cols if col in df_filter.columns]

st.dataframe(
    df_filter[papar_cols],
    use_container_width=True,
    hide_index=True
)

st.subheader("Semakan Data")

tab1, tab2, tab3 = st.tabs([
    "Baucar Tiada Nama / ID",
    "Duplicate Pergerakan",
    "Data Original"
])

with tab1:
    missing_info = df_filter[df_filter["NAMA"].isna() | df_filter["ID"].isna()]
    st.dataframe(missing_info, use_container_width=True, hide_index=True)

with tab2:
    duplicate_data = df_filter[df_filter.duplicated(subset=["NO_BAUCAR", "IN_OUT", "BULAN_TAHUN"], keep=False)]
    st.dataframe(duplicate_data, use_container_width=True, hide_index=True)

with tab3:
    st.write("Sheet BAUCAR")
    st.dataframe(baucar, use_container_width=True, hide_index=True)

    st.write("Sheet DATA APP")
    st.dataframe(data_app, use_container_width=True, hide_index=True)

csv = df_filter.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Data Dashboard CSV",
    csv,
    "dashboard_baucar_cidb.csv",
    "text/csv"
)
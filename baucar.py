import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Baucar CIDB", page_icon="📁", layout="wide")

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
df["ID"] = df["ID"].astype(str)

st.markdown("""
<div style="text-align:center; padding-top:20px; padding-bottom:20px;">
    <h1 style="font-size:56px;">Baucar CIDB</h1>
    <p style="font-size:22px; color:gray;">Sistem Pengurusan Keluar Masuk Baucar</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Filter")

tahun_list = sorted(df["TAHUN"].dropna().unique())
bulan_list = sorted(df["BULAN"].dropna().unique())
status_list = sorted(df["IN_OUT"].dropna().astype(str).unique())
id_list = sorted(df["ID"].dropna().unique())

tahun = st.sidebar.pills(
    "Tahun",
    tahun_list,
    default=tahun_list,
    selection_mode="multi"
)

bulan = st.sidebar.pills(
    "Bulan",
    bulan_list,
    default=bulan_list,
    selection_mode="multi"
)

status = st.sidebar.pills(
    "IN / OUT",
    status_list,
    default=status_list,
    selection_mode="multi"
)

id_filter = st.sidebar.pills(
    "ID",
    id_list,
    default=id_list,
    selection_mode="multi"
)

carian = st.sidebar.text_input("Cari Nama / No Baucar / Email / Kotak")

df_filter = df[
    df["TAHUN"].isin(tahun)
    & df["BULAN"].isin(bulan)
    & df["IN_OUT"].astype(str).isin(status)
    & df["ID"].isin(id_filter)
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

st.divider()

c1, c2 = st.columns(2)

with c1:
    chart_status = df_filter.groupby("IN_OUT").size().reset_index(name="Jumlah")
    fig_status = px.pie(
        chart_status,
        names="IN_OUT",
        values="Jumlah",
        title="IN vs OUT",
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
        title="Jumlah Baucar Mengikut ID"
    )
    st.plotly_chart(fig_id, use_container_width=True)

st.subheader("Senarai Perjalanan Baucar")

papar_cols = [
    "DATE", "IN_OUT", "BULAN_TAHUN", "NO_BAUCAR",
    "NAMA", "ID", "NO_KOTAK", "KOTAK_TAMBAHAN", "EMAIL"
]

papar_cols = [col for col in papar_cols if col in df_filter.columns]

st.dataframe(
    df_filter[papar_cols],
    use_container_width=True,
    hide_index=True
)

csv = df_filter.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Data CSV",
    csv,
    "dashboard_baucar_cidb.csv",
    "text/csv"
)
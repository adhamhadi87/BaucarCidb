import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Baucar CIDB", page_icon="📁", layout="wide")

BAUCAR_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1370653594&single=true&output=csv"
DATA_APP_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1657707039&single=true&output=csv"

ID_LOOKUP_FILE = "list ID.xlsx"


@st.cache_data(ttl=300)
def load_csv(url):
    df = pd.read_csv(url, dtype=str)
    df.columns = df.columns.astype(str).str.strip()
    return df


@st.cache_data(ttl=300)
def load_id_lookup(file_path):
    df = pd.read_excel(file_path, dtype=str)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df


def clean_text(series):
    return series.fillna("").astype(str).str.strip()


def clean_no_baucar(series):
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\s+", "", regex=True)
    )


def standardize_bulan(series):
    bulan_map = {
        "JAN": "JAN", "JANUARI": "JAN",
        "FEB": "FEB", "FEBRUARI": "FEB",
        "MAC": "MAC", "MAR": "MAC", "MARCH": "MAC",
        "APR": "APR", "APRIL": "APR",
        "MEI": "MEI", "MAY": "MEI",
        "JUN": "JUN", "JUNE": "JUN",
        "JUL": "JUL", "JULY": "JUL",
        "OGO": "OGO", "OGOS": "OGO", "AUG": "OGO", "AUGUST": "OGO",
        "SEP": "SEP", "SEPT": "SEP", "SEPTEMBER": "SEP",
        "OKT": "OKT", "OCT": "OKT", "OCTOBER": "OKT",
        "NOV": "NOV", "NOVEMBER": "NOV",
        "DIS": "DIS", "DEC": "DIS", "DECEMBER": "DIS"
    }

    extracted = series.fillna("").astype(str).str.extract(r"([A-Za-zÀ-ÿ]+)")[0]
    return extracted.fillna("").astype(str).str.upper().str.strip().map(bulan_map)


bulan_order = [
    "JAN", "FEB", "MAC", "APR", "MEI", "JUN",
    "JUL", "OGO", "SEP", "OKT", "NOV", "DIS"
]


baucar = load_csv(BAUCAR_CSV_URL)
data_app = load_csv(DATA_APP_CSV_URL)
id_lookup = load_id_lookup(ID_LOOKUP_FILE)

baucar = baucar.rename(columns={
    "BULAN/TAHUN": "BULAN_TAHUN",
    "NO BAUCAR": "NO_BAUCAR",
    "Name": "NAMA",
    "ID": "ID"
})

data_app = data_app.rename(columns={
    "DATE": "DATE",
    "IN/OUT": "IN_OUT",
    "BULAN /TAHUN": "BULAN_TAHUN_APP",
    "BULAN/TAHUN": "BULAN_TAHUN_APP",
    "NO. BAUCAR": "NO_BAUCAR",
    "NO BAUCAR": "NO_BAUCAR",
    "NO KOTAK": "NO_KOTAK",
    "KOTAK TAMBAHAN": "KOTAK_TAMBAHAN",
    "EMAIL": "EMAIL"
})

id_lookup = id_lookup.rename(columns={
    "NO STAF": "ID",
    "NO STAFF": "ID",
    "NAMA": "NAMA_ID",
    "NAME": "NAMA_ID"
})

required_baucar = ["BULAN_TAHUN", "NO_BAUCAR", "NAMA", "ID"]
required_data_app = ["NO_BAUCAR", "IN_OUT"]
required_lookup = ["ID", "NAMA_ID"]

missing_baucar = [c for c in required_baucar if c not in baucar.columns]
missing_data_app = [c for c in required_data_app if c not in data_app.columns]
missing_lookup = [c for c in required_lookup if c not in id_lookup.columns]

if missing_baucar:
    st.error(f"Column tidak dijumpai dalam sheet BAUCAR: {missing_baucar}")
    st.write("Column BAUCAR yang dibaca:", list(baucar.columns))
    st.stop()

if missing_data_app:
    st.error(f"Column tidak dijumpai dalam sheet DATA APP: {missing_data_app}")
    st.write("Column DATA APP yang dibaca:", list(data_app.columns))
    st.stop()

if missing_lookup:
    st.error(f"Column tidak dijumpai dalam list ID.xlsx: {missing_lookup}")
    st.write("Column list ID.xlsx yang dibaca:", list(id_lookup.columns))
    st.stop()

baucar["NO_BAUCAR_CLEAN"] = clean_no_baucar(baucar["NO_BAUCAR"])
baucar["ID"] = clean_text(baucar["ID"])
baucar["TAHUN"] = baucar["BULAN_TAHUN"].fillna("").astype(str).str.extract(r"(\d{4})")
baucar["BULAN"] = standardize_bulan(baucar["BULAN_TAHUN"])

data_app["NO_BAUCAR_CLEAN"] = clean_no_baucar(data_app["NO_BAUCAR"])
data_app = data_app[data_app["NO_BAUCAR_CLEAN"] != ""]
data_app["IN_OUT"] = clean_text(data_app["IN_OUT"]).str.upper()

id_lookup["ID"] = clean_text(id_lookup["ID"])
id_lookup["NAMA_ID"] = clean_text(id_lookup["NAMA_ID"])
id_lookup = id_lookup.drop_duplicates(subset=["ID"], keep="first")

if "DATE" in data_app.columns:
    data_app["DATE"] = pd.to_datetime(data_app["DATE"], errors="coerce", dayfirst=True)
    data_app = data_app.sort_values("DATE")

latest_app = data_app.drop_duplicates(subset=["NO_BAUCAR_CLEAN"], keep="last")

df = baucar.merge(
    latest_app,
    on="NO_BAUCAR_CLEAN",
    how="left",
    suffixes=("", "_APP")
)

df = df.merge(
    id_lookup[["ID", "NAMA_ID"]],
    on="ID",
    how="left"
)

df["STATUS_KEMASKINI"] = df["IN_OUT"]
df.loc[df["IN_OUT"].isna(), "STATUS_KEMASKINI"] = "BELUM DIKEMASKINI"

df["STATUS_KEMASKINI"] = (
    df["STATUS_KEMASKINI"]
    .fillna("BELUM DIKEMASKINI")
    .astype(str)
    .str.upper()
    .str.strip()
    .replace({
        "": "BELUM DIKEMASKINI",
        "NAN": "BELUM DIKEMASKINI",
        "NONE": "BELUM DIKEMASKINI"
    })
)

df["ID_FILTER_LABEL"] = df["NAMA_ID"].fillna("").astype(str).str.strip()
df.loc[df["ID_FILTER_LABEL"] == "", "ID_FILTER_LABEL"] = df["ID"]
df.loc[df["ID_FILTER_LABEL"].fillna("").astype(str).str.strip() == "", "ID_FILTER_LABEL"] = "(Blank)"

st.markdown("""
<div style="text-align:center; padding-top:20px; padding-bottom:20px;">
    <h1 style="font-size:56px;">Baucar CIDB</h1>
    <p style="font-size:22px; color:gray;">Sistem Pengurusan Keluar Masuk Baucar</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Filter")

tahun_list = sorted(df["TAHUN"].dropna().astype(str).unique())
bulan_list = [b for b in bulan_order if b in df["BULAN"].dropna().astype(str).unique()]
status_list = ["IN", "OUT", "BELUM DIKEMASKINI"]

id_options = (
    df["ID_FILTER_LABEL"]
    .dropna()
    .astype(str)
    .drop_duplicates()
    .sort_values()
    .tolist()
)

if "(Blank)" in id_options:
    id_options = [x for x in id_options if x != "(Blank)"] + ["(Blank)"]

tahun = st.sidebar.pills("Tahun", tahun_list, default=tahun_list, selection_mode="multi")
bulan = st.sidebar.pills("Bulan", bulan_list, default=bulan_list, selection_mode="multi")
status = st.sidebar.pills("Status", status_list, default=status_list, selection_mode="multi")
id_filter = st.sidebar.pills("Nama / ID", id_options, default=id_options, selection_mode="multi")

carian = st.sidebar.text_input("Cari Nama / No Baucar / Email / Kotak")

df_filter = df[
    df["TAHUN"].astype(str).isin(tahun)
    & df["BULAN"].astype(str).isin(bulan)
    & df["STATUS_KEMASKINI"].astype(str).isin(status)
    & df["ID_FILTER_LABEL"].astype(str).isin(id_filter)
]

if carian:
    df_filter = df_filter[
        df_filter.astype(str).apply(
            lambda row: row.str.contains(carian, case=False, na=False).any(),
            axis=1
        )
    ]

total_2024 = len(df_filter[df_filter["TAHUN"] == "2024"])
total_2025 = len(df_filter[df_filter["TAHUN"] == "2025"])
total_2026 = len(df_filter[df_filter["TAHUN"] == "2026"])
total_semua = len(df_filter)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Baucar 2024", f"{total_2024:,}")
col2.metric("Baucar 2025", f"{total_2025:,}")
col3.metric("Baucar 2026", f"{total_2026:,}")
col4.metric("Total Baucar", f"{total_semua:,}")

st.divider()

chart_id_total = (
    df_filter.groupby("ID_FILTER_LABEL")
    .size()
    .reset_index(name="Total Baucar")
    .sort_values("Total Baucar", ascending=False)
)

fig_id_total = px.bar(
    chart_id_total,
    x="ID_FILTER_LABEL",
    y="Total Baucar",
    text="Total Baucar",
    title="Nama / ID vs Total Baucar"
)

st.plotly_chart(fig_id_total, use_container_width=True)

c1, c2 = st.columns(2)

with c1:
    chart_status = df_filter.groupby("STATUS_KEMASKINI").size().reset_index(name="Jumlah")
    fig_status = px.pie(
        chart_status,
        names="STATUS_KEMASKINI",
        values="Jumlah",
        title="Status Baucar",
        hole=0.4
    )
    st.plotly_chart(fig_status, use_container_width=True)

with c2:
    chart_bulan = (
        df_filter.groupby(["TAHUN", "BULAN", "STATUS_KEMASKINI"], observed=True)
        .size()
        .reset_index(name="Jumlah")
    )

    fig_bulan = px.bar(
        chart_bulan,
        x="BULAN",
        y="Jumlah",
        color="STATUS_KEMASKINI",
        text="Jumlah",
        title="Status Baucar Mengikut Bulan",
        category_orders={"BULAN": bulan_order}
    )
    st.plotly_chart(fig_bulan, use_container_width=True)

tab1, tab2, tab3 = st.tabs([
    "Semua Baucar",
    "Telah Dikemaskini",
    "Belum Dikemaskini"
])

papar_cols = [
    "BULAN_TAHUN",
    "NO_BAUCAR",
    "NAMA",
    "ID",
    "NAMA_ID",
    "STATUS_KEMASKINI",
    "DATE",
    "NO_KOTAK",
    "KOTAK_TAMBAHAN",
    "EMAIL"
]

papar_cols = [col for col in papar_cols if col in df_filter.columns]

with tab1:
    st.dataframe(df_filter[papar_cols], use_container_width=True, hide_index=True)

with tab2:
    telah = df_filter[df_filter["STATUS_KEMASKINI"].isin(["IN", "OUT"])]
    st.dataframe(telah[papar_cols], use_container_width=True, hide_index=True)

with tab3:
    belum = df_filter[df_filter["STATUS_KEMASKINI"] == "BELUM DIKEMASKINI"]
    st.dataframe(belum[papar_cols], use_container_width=True, hide_index=True)

with st.expander("Semakan kiraan data"):
    st.write("Jumlah row BAUCAR dibaca:", len(baucar))
    st.write("Jumlah row selepas merge:", len(df))
    st.write("Jumlah row selepas filter:", len(df_filter))
    st.write("Jumlah ID kosong:", (df["ID"].fillna("").astype(str).str.strip() == "").sum())
    st.write("Jumlah ID berjaya dipadankan dengan list ID:", df["NAMA_ID"].notna().sum())

csv = df_filter.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Data CSV",
    csv,
    "dashboard_baucar_cidb.csv",
    "text/csv"
)
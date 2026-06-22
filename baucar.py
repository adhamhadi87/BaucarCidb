import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Baucar CIDB", page_icon="📁", layout="wide")

BAUCAR_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1370653594&single=true&output=csv"
DATA_APP_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1657707039&single=true&output=csv"
ID_LOOKUP_FILE = "list ID.xlsx"

st.markdown("""
<style>
/* Sidebar mirror/glow style */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8fbff 0%, #eef6ff 100%);
}

section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    border-radius: 14px;
    border: 1px solid rgba(30, 144, 255, 0.25);
    background: rgba(255, 255, 255, 0.75);
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.9),
        0 6px 18px rgba(30,144,255,0.08);
    backdrop-filter: blur(8px);
}

section[data-testid="stSidebar"] span[data-baseweb="tag"] {
    border-radius: 999px;
    background: linear-gradient(135deg, #dff3ff 0%, #ffffff 45%, #bfe7ff 100%);
    color: #064e7a;
    border: 1px solid rgba(14, 165, 233, 0.35);
    box-shadow:
        0 0 8px rgba(14, 165, 233, 0.35),
        inset 0 1px 1px rgba(255,255,255,0.95);
    font-weight: 600;
}

section[data-testid="stSidebar"] span[data-baseweb="tag"]::before {
    content: "✓ ";
    color: #0284c7;
    font-weight: 900;
}

section[data-testid="stSidebar"] button[kind="secondary"] {
    border-radius: 14px;
    background: linear-gradient(135deg, #e0f2fe, #ffffff, #bae6fd);
    border: 1px solid rgba(14, 165, 233, 0.45);
    box-shadow: 0 0 12px rgba(14, 165, 233, 0.25);
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)


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


bulan_order = ["JAN", "FEB", "MAC", "APR", "MEI", "JUN", "JUL", "OGO", "SEP", "OKT", "NOV", "DIS"]

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

df = baucar.merge(latest_app, on="NO_BAUCAR_CLEAN", how="left", suffixes=("", "_APP"))
df = df.merge(id_lookup[["ID", "NAMA_ID"]], on="ID", how="left")

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


def set_default_filters():
    st.session_state["tahun_filter"] = tahun_list
    st.session_state["bulan_filter"] = bulan_list
    st.session_state["status_filter"] = status_list
    st.session_state["id_filter"] = id_options


for key in ["tahun_filter", "bulan_filter", "status_filter", "id_filter"]:
    if key not in st.session_state:
        set_default_filters()
        break

tahun = st.sidebar.multiselect("Tahun", tahun_list, key="tahun_filter")
bulan = st.sidebar.multiselect("Bulan", bulan_list, key="bulan_filter")
status = st.sidebar.multiselect("Status", status_list, key="status_filter")
id_filter = st.sidebar.multiselect("Nama / ID", id_options, key="id_filter")

st.sidebar.button("Refresh Filter", on_click=set_default_filters, use_container_width=True)

df_filter = df[
    df["TAHUN"].astype(str).isin(tahun)
    & df["BULAN"].astype(str).isin(bulan)
    & df["STATUS_KEMASKINI"].astype(str).isin(status)
    & df["ID_FILTER_LABEL"].astype(str).isin(id_filter)
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

chart_id_df = df_filter.copy()
chart_id_df["ID_PAPAR"] = chart_id_df["ID"].fillna("").astype(str).str.strip()
chart_id_df.loc[chart_id_df["ID_PAPAR"] == "", "ID_PAPAR"] = "(Blank)"

chart_id_total = (
    chart_id_df.groupby("ID_PAPAR", dropna=False)
    .size()
    .reset_index(name="Total Baucar")
    .sort_values("Total Baucar", ascending=False)
)

id_order = chart_id_total["ID_PAPAR"].tolist()

fig_id_total = px.bar(
    chart_id_total,
    x="ID_PAPAR",
    y="Total Baucar",
    text="Total Baucar",
    title="Total",
    category_orders={"ID_PAPAR": id_order}
)

fig_id_total.update_xaxes(type="category")
fig_id_total.update_layout(
    xaxis_title="ID",
    yaxis_title="Total Baucar"
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

tab1, tab2, tab3 = st.tabs(["Semua Baucar", "Telah Dikemaskini", "Belum Dikemaskini"])

papar_cols = [
    "BULAN_TAHUN", "NO_BAUCAR", "NAMA", "ID", "NAMA_ID",
    "STATUS_KEMASKINI", "DATE", "NO_KOTAK", "KOTAK_TAMBAHAN", "EMAIL"
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

csv = df_filter.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Data CSV",
    csv,
    "dashboard_baucar_cidb.csv",
    "text/csv"
)
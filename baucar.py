import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Baucar CIDB", page_icon="📁", layout="wide")

BAUCAR_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1370653594&single=true&output=csv"
DATA_APP_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1657707039&single=true&output=csv"
ID_LOOKUP_FILE = "list ID.xlsx"

st.markdown("""
<style>
/* =========================
   CIDB RED MIRROR PILL THEME
   Default kosong = semua data.
   Bila klik pill, hanya pilihan itu aktif.
   Klik semula pill aktif untuk untick.
========================= */

.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef6ff 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(239,68,68,0.22), transparent 28%),
        radial-gradient(circle at bottom right, rgba(248,113,113,0.18), transparent 30%),
        linear-gradient(180deg, #0f172a 0%, #111827 48%, #1e293b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.10);
}

/* Sidebar text */
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #f8fafc !important;
}

/* Pill container spacing */
section[data-testid="stSidebar"] div[data-testid="stPills"] {
    gap: 0.35rem !important;
}

/* Semua pill: gelap, tulisan jelas */
section[data-testid="stSidebar"] button[aria-pressed],
section[data-testid="stSidebar"] div[data-testid="stPills"] button,
section[data-testid="stSidebar"] div[data-baseweb="button-group"] button {
    background: rgba(255,255,255,0.075) !important;
    border: 1px solid rgba(255,255,255,0.24) !important;
    color: #f8fafc !important;
    border-radius: 999px !important;
    font-weight: 800 !important;
    padding: 0.45rem 0.85rem !important;
    margin-bottom: 0.25rem !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.10),
        0 4px 12px rgba(0,0,0,0.12) !important;
    transition: all 0.18s ease-in-out !important;
}

/* Pastikan tulisan dalam pill nampak */
section[data-testid="stSidebar"] button[aria-pressed] *,
section[data-testid="stSidebar"] div[data-testid="stPills"] button *,
section[data-testid="stSidebar"] div[data-baseweb="button-group"] button * {
    color: #f8fafc !important;
    font-weight: 800 !important;
}

/* Hover */
section[data-testid="stSidebar"] button[aria-pressed="false"]:hover,
section[data-testid="stSidebar"] div[data-testid="stPills"] button:hover,
section[data-testid="stSidebar"] div[data-baseweb="button-group"] button:hover {
    border: 1px solid rgba(248,113,113,0.95) !important;
    box-shadow:
        0 0 12px rgba(239,68,68,0.35),
        inset 0 1px 0 rgba(255,255,255,0.16) !important;
    transform: translateY(-1px);
}

/* Selected: merah mirror stay */
section[data-testid="stSidebar"] button[aria-pressed="true"],
section[data-testid="stSidebar"] button[aria-selected="true"],
section[data-testid="stSidebar"] div[data-testid="stPills"] button[aria-pressed="true"],
section[data-testid="stSidebar"] div[data-testid="stPills"] button[aria-selected="true"],
section[data-testid="stSidebar"] div[data-baseweb="button-group"] button[aria-pressed="true"],
section[data-testid="stSidebar"] div[data-baseweb="button-group"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #991b1b 0%, #dc2626 42%, #ef4444 72%, #fca5a5 100%) !important;
    border: 2px solid rgba(255,255,255,0.96) !important;
    color: #ffffff !important;
    font-weight: 900 !important;
    box-shadow:
        0 0 8px rgba(220,38,38,0.92),
        0 0 18px rgba(239,68,68,0.78),
        0 0 34px rgba(248,113,113,0.58),
        inset 0 1px 0 rgba(255,255,255,0.58),
        inset 0 -10px 18px rgba(127,29,29,0.24) !important;
}

/* Text selected */
section[data-testid="stSidebar"] button[aria-pressed="true"] *,
section[data-testid="stSidebar"] button[aria-selected="true"] *,
section[data-testid="stSidebar"] div[data-testid="stPills"] button[aria-pressed="true"] *,
section[data-testid="stSidebar"] div[data-testid="stPills"] button[aria-selected="true"] * {
    color: #ffffff !important;
    font-weight: 900 !important;
}

/* Tick indicator for selected pill */
section[data-testid="stSidebar"] button[aria-pressed="true"]::before,
section[data-testid="stSidebar"] button[aria-selected="true"]::before {
    content: "✓ ";
    font-weight: 950;
    color: #ffffff;
}

/* Refresh button */
section[data-testid="stSidebar"] div.stButton > button {
    background: linear-gradient(135deg, #991b1b 0%, #dc2626 52%, #f87171 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.90) !important;
    border-radius: 14px !important;
    font-weight: 900 !important;
    box-shadow:
        0 0 14px rgba(220,38,38,0.36),
        0 0 24px rgba(248,113,113,0.30) !important;
}

section[data-testid="stSidebar"] div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow:
        0 0 18px rgba(220,38,38,0.50),
        0 0 34px rgba(248,113,113,0.44) !important;
}

/* KPI cards */
[data-testid="metric-container"] {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 20px;
    padding: 18px;
    box-shadow: 0 10px 28px rgba(15,23,42,0.08);
}

/* Charts */
[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.88);
    border-radius: 18px;
    padding: 8px;
    box-shadow: 0 8px 22px rgba(15,23,42,0.06);
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 8px 22px rgba(15,23,42,0.06);
}

button[data-baseweb="tab"] {
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

st.sidebar.title("✨ Filter")

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
    # Kosong bermaksud semua data dipaparkan.
    # Bila user klik pill, pilihan itu sahaja aktif.
    st.session_state["tahun_filter"] = []
    st.session_state["bulan_filter"] = []
    st.session_state["status_filter"] = []
    st.session_state["id_filter"] = []


for key in ["tahun_filter", "bulan_filter", "status_filter", "id_filter"]:
    if key not in st.session_state:
        set_default_filters()
        break

st.sidebar.markdown("#### Tahun")
tahun = st.sidebar.pills("Tahun", tahun_list, selection_mode="multi", key="tahun_filter", label_visibility="collapsed")

st.sidebar.markdown("#### Bulan")
bulan = st.sidebar.pills("Bulan", bulan_list, selection_mode="multi", key="bulan_filter", label_visibility="collapsed")

st.sidebar.markdown("#### Status")
status = st.sidebar.pills("Status", status_list, selection_mode="multi", key="status_filter", label_visibility="collapsed")

st.sidebar.markdown("#### Nama / ID")
id_filter = st.sidebar.pills("Nama / ID", id_options, selection_mode="multi", key="id_filter", label_visibility="collapsed")

st.sidebar.button("Refresh Filter", on_click=set_default_filters, use_container_width=True)

tahun_selected = tahun if tahun else tahun_list
bulan_selected = bulan if bulan else bulan_list
status_selected = status if status else status_list
id_selected = id_filter if id_filter else id_options

df_filter = df[
    df["TAHUN"].astype(str).isin(tahun_selected)
    & df["BULAN"].astype(str).isin(bulan_selected)
    & df["STATUS_KEMASKINI"].astype(str).isin(status_selected)
    & df["ID_FILTER_LABEL"].astype(str).isin(id_selected)
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
fig_id_total.update_layout(xaxis_title="ID", yaxis_title="Total Baucar")

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
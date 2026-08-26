
import streamlit as st
import pandas as pd
import plotly.express as px
import re
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from io import StringIO

st.set_page_config(page_title="i-FILING BKA", page_icon="📁", layout="wide")

BAUCAR_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1370653594&single=true&output=csv"
APPLIKASI_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1571972700&single=true&output=csv"

# GANTIKAN GID_SHEET_EMEL dengan gid sebenar tab "emel"
EMEL_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1298317374&single=true&output=csv"

ID_LOOKUP_FILE = "list ID.xlsx"

st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #eef6ff 100%);
}

.block-container {
    padding-top: 0.8rem !important;
    padding-bottom: 1rem !important;
    max-width: 1500px !important;
}

section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top left, rgba(239,68,68,0.24), transparent 28%),
        radial-gradient(circle at bottom right, rgba(248,113,113,0.20), transparent 30%),
        linear-gradient(180deg, #0f172a 0%, #111827 48%, #1e293b 100%) !important;
    border-right: 1px solid rgba(255,255,255,0.10);
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
    color: #f8fafc !important;
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-pills"],
section[data-testid="stSidebar"] button[aria-pressed="false"],
section[data-testid="stSidebar"] button[aria-selected="false"] {
    background: rgba(255,255,255,0.075) !important;
    border: 1px solid rgba(255,255,255,0.22) !important;
    color: #e5e7eb !important;
    border-radius: 999px !important;
    font-weight: 800 !important;
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.10),
        0 4px 12px rgba(0,0,0,0.12) !important;
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-pills"] *,
section[data-testid="stSidebar"] button[aria-pressed="false"] *,
section[data-testid="stSidebar"] button[aria-selected="false"] * {
    color: #e5e7eb !important;
    font-weight: 800 !important;
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-pillsActive"],
section[data-testid="stSidebar"] button[aria-pressed="true"],
section[data-testid="stSidebar"] button[aria-selected="true"],
section[data-testid="stSidebar"] button[aria-checked="true"] {
    background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 42%, #ef4444 72%, #fecaca 100%) !important;
    border: 2px solid #ffffff !important;
    color: #ffffff !important;
    border-radius: 999px !important;
    font-weight: 950 !important;
    box-shadow:
        0 0 10px rgba(220,38,38,0.95),
        0 0 22px rgba(239,68,68,0.85),
        0 0 42px rgba(248,113,113,0.65),
        inset 0 1px 0 rgba(255,255,255,0.72),
        inset 0 -10px 18px rgba(127,29,29,0.28) !important;
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-pillsActive"] *,
section[data-testid="stSidebar"] button[aria-pressed="true"] *,
section[data-testid="stSidebar"] button[aria-selected="true"] *,
section[data-testid="stSidebar"] button[aria-checked="true"] * {
    color: #ffffff !important;
    font-weight: 950 !important;
}

section[data-testid="stSidebar"] button[data-testid="stBaseButton-pillsActive"]::before,
section[data-testid="stSidebar"] button[aria-pressed="true"]::before,
section[data-testid="stSidebar"] button[aria-selected="true"]::before,
section[data-testid="stSidebar"] button[aria-checked="true"]::before {
    content: "✓ ";
    font-weight: 950;
    color: #ffffff;
}

section[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(135deg, #7f1d1d 0%, #dc2626 52%, #f87171 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.90) !important;
    border-radius: 14px !important;
    font-weight: 900 !important;
}

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.94);
    border: 1px solid rgba(15,23,42,0.08);
    border-radius: 20px;
    padding: 12px 16px !important;
    box-shadow: 0 10px 28px rgba(15,23,42,0.08);
}

[data-testid="stMetricValue"] {
    font-size: 2.05rem !important;
}

[data-testid="stPlotlyChart"] {
    background: rgba(255,255,255,0.88);
    border-radius: 18px;
    padding: 8px;
    box-shadow: 0 8px 22px rgba(15,23,42,0.06);
}

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



# =========================
# PASSWORD PROTECTION
# =========================
# Streamlit Cloud:
# Settings > Secrets
# APP_PASSWORD = "password_anda"
DEFAULT_PASSWORD = "bka123"

try:
    APP_PASSWORD = st.secrets["APP_PASSWORD"]
except Exception:
    APP_PASSWORD = DEFAULT_PASSWORD


def login_screen():
    st.markdown("""
    <div style="max-width:520px; margin:70px auto 20px auto; padding:30px;
                background:white; border-radius:22px;
                box-shadow:0 15px 40px rgba(15,23,42,0.12); text-align:center;">
        <h1 style="margin-bottom:6px;">i-FiLiNG BKA</h1>
        <p style="color:gray; margin-top:0;">Sila masukkan password untuk akses dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Masuk", use_container_width=True)

        if submit:
            if password == APP_PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Password salah. Sila cuba semula.")


if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    login_screen()
    st.stop()




@st.cache_data(ttl=3600, show_spinner=False)
def load_csv(url, header="infer"):
    """
    Baca Google Sheet CSV dengan retry automatik.
    Cache 1 jam supaya dashboard tidak download semula setiap kali filter/tab berubah.
    """

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv,text/plain,*/*",
        "Connection": "keep-alive",
    }

    retry_strategy = Retry(
        total=3,
        connect=3,
        read=3,
        backoff_factor=1.5,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET"],
        raise_on_status=False,
    )

    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    try:
        response = session.get(
            url,
            headers=headers,
            timeout=(15, 120),
            allow_redirects=True,
        )
    except requests.exceptions.ReadTimeout as exc:
        raise RuntimeError(
            "Google Sheet mengambil masa terlalu lama untuk dibaca. "
            "Sila cuba Refresh Data sekali lagi."
        ) from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"Gagal baca Google Sheet: HTTP {response.status_code} | "
            f"URL akhir: {response.url}"
        )

    content = response.text

    if not content.strip():
        raise RuntimeError("Google Sheet kosong.")

    df = pd.read_csv(
        StringIO(content),
        dtype=str,
        header=header
    )

    if header is not None:
        df.columns = df.columns.astype(str).str.strip()

    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_id_lookup(file_path):
    df = pd.read_excel(file_path, dtype=str)
    df.columns = df.columns.astype(str).str.strip().str.upper()
    return df


def clean_text(series):
    return series.fillna("").astype(str).str.strip()


def clean_no_baucar(series):
    cleaned = (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"[^A-Z0-9]", "", regex=True)
    )

    cleaned = cleaned.apply(
        lambda x: str(int(x)) if isinstance(x, str) and x.isdigit() and x != "" else x
    )

    return cleaned


def normalize_status(series):
    return (
        series.fillna("")
        .astype(str)
        .str.upper()
        .str.strip()
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
        "JUL": "JUL", "JULY": "JUL", "JULAI": "JUL",
        "OGO": "OGO", "OGOS": "OGO", "AUG": "OGO", "AUGUST": "OGO",
        "SEP": "SEP", "SEPT": "SEP", "SEPTEMBER": "SEP",
        "OKT": "OKT", "OCT": "OKT", "OCTOBER": "OKT",
        "NOV": "NOV", "NOVEMBER": "NOV",
        "DIS": "DIS", "DEC": "DIS", "DECEMBER": "DIS"
    }
    extracted = series.fillna("").astype(str).str.extract(r"([A-Za-zÀ-ÿ]+)")[0]
    return extracted.fillna("").astype(str).str.upper().str.strip().map(bulan_map)


def parse_bulan_tahun_aging(series):
    """
    Parser KHAS untuk Aging sahaja.
    Tidak mengubah BULAN / TAHUN yang digunakan dashboard utama.

    Sokong nama bulan dan format nombor seperti:
    JAN 2026, JULAI 2026, OGOS/2026, 08/2026, 2026-08.
    """
    month_name_map = {
        "JAN": 1, "JANUARI": 1, "JANUARY": 1,
        "FEB": 2, "FEBRUARI": 2, "FEBRUARY": 2,
        "MAC": 3, "MAR": 3, "MARCH": 3,
        "APR": 4, "APRIL": 4,
        "MEI": 5, "MAY": 5,
        "JUN": 6, "JUNE": 6,
        "JUL": 7, "JULAI": 7, "JULY": 7,
        "OGO": 8, "OGOS": 8, "AUG": 8, "AUGUST": 8,
        "SEP": 9, "SEPT": 9, "SEPTEMBER": 9,
        "OKT": 10, "OCT": 10, "OCTOBER": 10,
        "NOV": 11, "NOVEMBER": 11,
        "DIS": 12, "DEC": 12, "DECEMBER": 12
    }

    def parse_one(value):
        if pd.isna(value):
            return pd.Series([pd.NA, pd.NA])

        s = str(value).strip().upper()
        if not s:
            return pd.Series([pd.NA, pd.NA])

        year_match = re.search(r"(20\d{2})", s)
        year = int(year_match.group(1)) if year_match else None

        month = None
        for name, num in month_name_map.items():
            if re.search(rf"(?<![A-Z]){re.escape(name)}(?![A-Z])", s):
                month = num
                break

        if month is None:
            m = re.search(r"(?<!\d)(0?[1-9]|1[0-2])\s*[/-]\s*(20\d{2})(?!\d)", s)
            if m:
                month = int(m.group(1))
                year = int(m.group(2))

        if month is None:
            m = re.search(r"(?<!\d)(20\d{2})\s*[/-]\s*(0?[1-9]|1[0-2])(?!\d)", s)
            if m:
                year = int(m.group(1))
                month = int(m.group(2))

        return pd.Series([month, year])

    parsed = series.apply(parse_one)
    parsed.columns = ["AGING_MONTH_NUM", "AGING_YEAR_NUM"]
    return parsed

def bulan_tahun_to_date(bulan_series, tahun_series):
    """
    Tukar BULAN + TAHUN kepada tarikh rujukan hari pertama bulan.
    Digunakan untuk kira aging baucar.
    """
    month_num_map = {
        "JAN": 1, "FEB": 2, "MAC": 3, "APR": 4,
        "MEI": 5, "JUN": 6, "JUL": 7, "OGO": 8,
        "SEP": 9, "OKT": 10, "NOV": 11, "DIS": 12
    }

    bulan_num = bulan_series.map(month_num_map)
    tahun_num = pd.to_numeric(tahun_series, errors="coerce")

    result = pd.to_datetime(
        dict(
            year=tahun_num,
            month=bulan_num,
            day=1
        ),
        errors="coerce"
    )

    return result


def kira_umur_bulan_dari_bulan_tahun(bulan_series, tahun_series, tarikh_rujukan=None):
    """
    Kira umur baucar terus daripada BULAN + TAHUN.
    Kaedah ini lebih robust berbanding bergantung pada conversion tarikh penuh.
    """
    if tarikh_rujukan is None:
        tarikh_rujukan = pd.Timestamp.today().normalize()

    month_num_map = {
        "JAN": 1, "FEB": 2, "MAC": 3, "APR": 4,
        "MEI": 5, "JUN": 6, "JUL": 7, "OGO": 8,
        "SEP": 9, "OKT": 10, "NOV": 11, "DIS": 12
    }

    bulan_num = pd.to_numeric(bulan_series.map(month_num_map), errors="coerce")
    tahun_num = pd.to_numeric(tahun_series, errors="coerce")

    umur = (
        (tarikh_rujukan.year - tahun_num) * 12
        + (tarikh_rujukan.month - bulan_num)
    )

    return umur

def kategori_aging(umur_bulan):
    """
    Kategori aging ringkas.
    Semua baucar BELUM DIKEMASKINI dimasukkan dalam Aging,
    termasuk baucar berumur 0-3 bulan.
    """
    if pd.isna(umur_bulan):
        return "TARIKH TIDAK SAH"

    umur_bulan = int(umur_bulan)

    if umur_bulan < 3:
        return "0-3 BULAN"
    if umur_bulan < 6:
        return "3-6 BULAN"
    if umur_bulan < 9:
        return "6-9 BULAN"
    if umur_bulan < 12:
        return "9-12 BULAN"

    return ">1 TAHUN"

def aging_sort_key(label):
    """
    Susun kategori aging dengan betul.
    """
    sort_map = {
        "0-3 BULAN": 0,
        "3-6 BULAN": 3,
        "6-9 BULAN": 6,
        "9-12 BULAN": 9,
        ">1 TAHUN": 12,
        "TARIKH TIDAK SAH": 9999
    }
    return sort_map.get(str(label), 9998)


bulan_order = ["JAN", "FEB", "MAC", "APR", "MEI", "JUN", "JUL", "OGO", "SEP", "OKT", "NOV", "DIS"]

with st.spinner("Memuatkan data i-Filing BKA..."):
    # Muat satu per satu supaya Google Sheet tidak menerima 3 request serentak.
    # Cache 1 jam: selepas load pertama berjaya, filter/tab seterusnya sangat cepat.
    baucar = load_csv(BAUCAR_CSV_URL)
    aplikasi = load_csv(APPLIKASI_CSV_URL)
    emel = load_csv(EMEL_CSV_URL)
    id_lookup = load_id_lookup(ID_LOOKUP_FILE)

baucar = baucar.rename(columns={
    "BULAN/TAHUN": "BULAN_TAHUN",
    "NO BAUCAR": "NO_BAUCAR",
    "Name": "NAMA",
    "ID": "ID"
})

aplikasi = aplikasi.rename(columns={
    "TIMESTAMP": "DATE",
    "DATE": "DATE",
    "IN / OUT": "IN_OUT",
    "IN/OUT": "IN_OUT",
    "IN OUT": "IN_OUT",
    "BULAN / TAHUN": "BULAN_TAHUN_APP",
    "BULAN /TAHUN": "BULAN_TAHUN_APP",
    "BULAN/TAHUN": "BULAN_TAHUN_APP",
    "NO BAUCAR": "NO_BAUCAR",
    "NO. BAUCAR": "NO_BAUCAR",
    "NO KOTAK": "NO_KOTAK",
    "KOTAK TAMBAHAN": "KOTAK_TAMBAHAN",
    "EMAIL": "EMAIL"
})

# SHEET EMEL
# Sokong dua keadaan:
# 1. Ada header ID / NAMA / EMAIL
# 2. Tiada header, data terus bermula pada row pertama

emel.columns = emel.columns.astype(str).str.strip()
emel_upper_map = {str(c).strip().upper(): c for c in emel.columns}

email_id_col = next((emel_upper_map[x] for x in ["ID", "NO STAF", "NO STAFF"] if x in emel_upper_map), None)
email_name_col = next((emel_upper_map[x] for x in ["NAMA", "NAME"] if x in emel_upper_map), None)
email_addr_col = next((emel_upper_map[x] for x in ["EMAIL", "E-MAIL", "EMEL"] if x in emel_upper_map), None)

if email_id_col is None or email_addr_col is None:
    emel = load_csv(EMEL_CSV_URL, header=None)
    emel = emel.iloc[:, :3].copy()
    if emel.shape[1] < 3:
        st.error("Sheet emel perlu ada sekurang-kurangnya 3 column: ID, NAMA, EMAIL.")
        st.stop()
    emel.columns = ["ID", "NAMA_EMEL", "EMAIL_PEMILIK"]
else:
    rename_emel = {
        email_id_col: "ID",
        email_addr_col: "EMAIL_PEMILIK"
    }
    if email_name_col is not None:
        rename_emel[email_name_col] = "NAMA_EMEL"
    emel = emel.rename(columns=rename_emel)
    if "NAMA_EMEL" not in emel.columns:
        emel["NAMA_EMEL"] = ""

id_lookup = id_lookup.rename(columns={
    "NO STAF": "ID",
    "NO STAFF": "ID",
    "NAMA": "NAMA_ID",
    "NAME": "NAMA_ID"
})

required_baucar = ["BULAN_TAHUN", "NO_BAUCAR", "NAMA", "ID"]
required_aplikasi = ["NO_BAUCAR", "IN_OUT"]
required_lookup = ["ID", "NAMA_ID"]
required_emel = ["ID", "EMAIL_PEMILIK"]

missing_baucar = [c for c in required_baucar if c not in baucar.columns]
missing_aplikasi = [c for c in required_aplikasi if c not in aplikasi.columns]
missing_lookup = [c for c in required_lookup if c not in id_lookup.columns]
missing_emel = [c for c in required_emel if c not in emel.columns]

if missing_baucar:
    st.error(f"Column tidak dijumpai dalam sheet BAUCAR: {missing_baucar}")
    st.write("Column BAUCAR yang dibaca:", list(baucar.columns))
    st.stop()

if missing_aplikasi:
    st.error(f"Column tidak dijumpai dalam sheet APPLIKASI: {missing_aplikasi}")
    st.write("Column APPLIKASI yang dibaca:", list(aplikasi.columns))
    st.stop()

if missing_lookup:
    st.error(f"Column tidak dijumpai dalam list ID.xlsx: {missing_lookup}")
    st.write("Column list ID.xlsx yang dibaca:", list(id_lookup.columns))
    st.stop()

if missing_emel:
    st.error(f"Column tidak dijumpai dalam sheet emel: {missing_emel}")
    st.write("Column sheet emel yang dibaca:", list(emel.columns))
    st.stop()

# Master BAUCAR
baucar["NO_BAUCAR_CLEAN"] = clean_no_baucar(baucar["NO_BAUCAR"])
baucar["ID"] = clean_text(baucar["ID"])
baucar["TAHUN"] = baucar["BULAN_TAHUN"].fillna("").astype(str).str.extract(r"(\d{4})")
baucar["BULAN"] = standardize_bulan(baucar["BULAN_TAHUN"])

# APPLIKASI
# Sheet APPLIKASI ialah source sebenar.
# Column NO_BAUCAR mengandungi banyak baucar dalam satu cell dipisahkan dengan koma.
# Jadi Python akan pecahkan kepada 1 row = 1 baucar.

aplikasi["NO_BAUCAR_RAW"] = aplikasi["NO_BAUCAR"].fillna("").astype(str)

aplikasi["NO_BAUCAR_LIST"] = (
    aplikasi["NO_BAUCAR_RAW"]
    .str.split(",")
)

aplikasi = aplikasi.explode("NO_BAUCAR_LIST").copy()

aplikasi["NO_BAUCAR"] = aplikasi["NO_BAUCAR_LIST"]
aplikasi["NO_BAUCAR_CLEAN"] = clean_no_baucar(aplikasi["NO_BAUCAR"])

aplikasi = aplikasi[
    (aplikasi["NO_BAUCAR_CLEAN"] != "")
    & (aplikasi["NO_BAUCAR_CLEAN"] != "LOADING")
].copy()

aplikasi["IN_OUT"] = normalize_status(aplikasi["IN_OUT"])
aplikasi.loc[~aplikasi["IN_OUT"].isin(["IN", "OUT"]), "IN_OUT"] = ""

if "DATE" in aplikasi.columns:
    aplikasi["DATE"] = pd.to_datetime(aplikasi["DATE"], errors="coerce", dayfirst=True)

# Lookup ID
id_lookup["ID"] = clean_text(id_lookup["ID"])
id_lookup["NAMA_ID"] = clean_text(id_lookup["NAMA_ID"])
id_lookup = id_lookup.drop_duplicates(subset=["ID"], keep="first")

# Lookup email pemilik ikut ID dari sheet "emel"
emel["ID"] = clean_text(emel["ID"]).str.replace(r"\.0$", "", regex=True)
emel["NAMA_EMEL"] = clean_text(emel["NAMA_EMEL"])
emel["EMAIL_PEMILIK"] = clean_text(emel["EMAIL_PEMILIK"]).str.lower()

emel = emel[
    (emel["ID"] != "")
    & (emel["ID"].str.upper() != "ID")
    & (emel["EMAIL_PEMILIK"].str.upper() != "EMAIL")
].copy()

emel = emel.drop_duplicates(subset=["ID"], keep="first")

# ======================================================================
# STATUS LOGIC - FINAL LOCKED
#
# IN  = NO BAUCAR ada dalam APPLIKASI dan status terkini IN
# OUT = NO BAUCAR ada dalam APPLIKASI dan status terkini OUT
# BELUM DIKEMASKINI = NO BAUCAR ada dalam BAUCAR tetapi tiada dalam APPLIKASI
#
# JANGAN TUKAR LOGIC INI
# ======================================================================

# Row asal APPLIKASI digunakan untuk tentukan status terkini.
# Rekod paling bawah bagi NO BAUCAR yang sama = status terkini.
aplikasi["_ROW_ORDER"] = range(len(aplikasi))

# Semua NO BAUCAR yang wujud dalam APPLIKASI
app_set = set(aplikasi["NO_BAUCAR_CLEAN"])

# Hanya row yang statusnya sah IN / OUT digunakan untuk status terkini
valid_status_app = aplikasi[aplikasi["IN_OUT"].isin(["IN", "OUT"])].copy()

latest_status = valid_status_app.sort_values("_ROW_ORDER").drop_duplicates(
    subset=["NO_BAUCAR_CLEAN"],
    keep="last"
).copy()

# Detail terkini untuk DATE / KOTAK / EMAIL ikut row terakhir APPLIKASI
latest_app = aplikasi.sort_values("_ROW_ORDER").drop_duplicates(
    subset=["NO_BAUCAR_CLEAN"],
    keep="last"
).copy()

latest_cols = [
    c for c in [
        "NO_BAUCAR_CLEAN",
        "DATE",
        "NO_KOTAK",
        "KOTAK_TAMBAHAN",
        "EMAIL",
        "BULAN_TAHUN_APP"
    ]
    if c in latest_app.columns
]

df = baucar.merge(latest_app[latest_cols], on="NO_BAUCAR_CLEAN", how="left")

if not latest_status.empty:
    df = df.merge(
        latest_status[["NO_BAUCAR_CLEAN", "IN_OUT"]],
        on="NO_BAUCAR_CLEAN",
        how="left"
    )
else:
    df["IN_OUT"] = ""

df = df.merge(id_lookup[["ID", "NAMA_ID"]], on="ID", how="left")

# Padankan ID BAUCAR dengan NAMA + EMAIL daripada sheet "emel"
df = df.merge(
    emel[["ID", "NAMA_EMEL", "EMAIL_PEMILIK"]],
    on="ID",
    how="left"
)

df["ADA_APLIKASI"] = df["NO_BAUCAR_CLEAN"].isin(app_set)

df["STATUS_KEMASKINI"] = "BELUM DIKEMASKINI"
df.loc[df["ADA_APLIKASI"] & (df["IN_OUT"] == "IN"), "STATUS_KEMASKINI"] = "IN"
df.loc[df["ADA_APLIKASI"] & (df["IN_OUT"] == "OUT"), "STATUS_KEMASKINI"] = "OUT"

df["TELAH_DIKEMASKINI"] = df["STATUS_KEMASKINI"].isin(["IN", "OUT"])


# ==========================================================
# AGING BAUCAR
# Kiraan terus dalam Streamlit - tiada sheet tambahan diperlukan.
# Rujukan umur berdasarkan BULAN_TAHUN dalam sheet BAUCAR.
# ==========================================================
# Aging dikira secara BERASINGAN daripada filter Tahun/Bulan dashboard utama.
# Ini memastikan perubahan Aging tidak boleh mengosongkan data dashboard utama.
aging_parsed = parse_bulan_tahun_aging(df["BULAN_TAHUN"])
df["AGING_MONTH_NUM"] = pd.to_numeric(aging_parsed["AGING_MONTH_NUM"], errors="coerce")
df["AGING_YEAR_NUM"] = pd.to_numeric(aging_parsed["AGING_YEAR_NUM"], errors="coerce")

_today_aging = pd.Timestamp.today().normalize()
df["UMUR_BULAN"] = (
    (_today_aging.year - df["AGING_YEAR_NUM"]) * 12
    + (_today_aging.month - df["AGING_MONTH_NUM"])
)

df["KATEGORI_AGING"] = df["UMUR_BULAN"].apply(kategori_aging)

df["ID_FILTER_LABEL"] = df["NAMA_ID"].fillna("").astype(str).str.strip()
df.loc[df["ID_FILTER_LABEL"] == "", "ID_FILTER_LABEL"] = df["ID"]
df.loc[df["ID_FILTER_LABEL"].fillna("").astype(str).str.strip() == "", "ID_FILTER_LABEL"] = "(Blank)"

st.markdown("""
<div style="text-align:center; padding-top:0px; padding-bottom:8px;">
    <h1 style="font-size:46px; margin-bottom:2px;">i-FILING BKA</h1>
    <p style="font-size:18px; color:gray; margin-top:0px;">Sistem Pengurusan Keluar Masuk Baucar</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("✨ Filter")
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["authenticated"] = False
    st.rerun()

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
    # Kosong = semua data dipaparkan
    st.session_state["tahun_filter"] = []
    st.session_state["bulan_filter"] = []
    st.session_state["status_filter"] = []
    st.session_state["id_filter"] = []


def refresh_all():
    # Reset filter + paksa baca semula Google Sheet
    st.cache_data.clear()
    set_default_filters()
    st.rerun()


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

st.sidebar.button("Reset Filter + Refresh Data", on_click=refresh_all, use_container_width=True)

tahun_selected = tahun if tahun else tahun_list
bulan_selected = bulan if bulan else bulan_list
id_selected = id_filter if id_filter else id_options

df_filter = df[
    df["TAHUN"].astype(str).isin(tahun_selected)
    & df["BULAN"].astype(str).isin(bulan_selected)
    & df["ID_FILTER_LABEL"].astype(str).isin(id_selected)
].copy()

# Status filter:
# Kosong = semua status
# IN = status terkini IN
# OUT = status terkini OUT
# BELUM DIKEMASKINI = tiada dalam DATA APP
if status:
    df_filter = df_filter[
        df_filter["STATUS_KEMASKINI"].astype(str).isin(status)
    ].copy()

total_2024 = len(df_filter[df_filter["TAHUN"] == "2024"])
total_2025 = len(df_filter[df_filter["TAHUN"] == "2025"])
total_2026 = len(df_filter[df_filter["TAHUN"] == "2026"])
total_semua = len(df_filter)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Baucar 2024", f"{total_2024:,}")
col2.metric("Baucar 2025", f"{total_2025:,}")
col3.metric("Baucar 2026", f"{total_2026:,}")
col4.metric("Total Baucar", f"{total_semua:,}")

st.markdown("<hr style='margin: 0.5rem 0 1rem 0;'>", unsafe_allow_html=True)

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
    yaxis_title="Total Baucar",
    height=430,
    margin=dict(l=35, r=20, t=45, b=45),
    title=dict(font=dict(size=18))
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
    fig_status.update_layout(height=360, margin=dict(l=20, r=20, t=45, b=20))
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
    fig_bulan.update_layout(height=360, margin=dict(l=30, r=20, t=45, b=35))
    st.plotly_chart(fig_bulan, use_container_width=True)

tab1, tab2, tab3, tab4 = st.tabs(["Semua Baucar", "Telah Dikemaskini", "Belum Dikemaskini", "Aging Baucar"])

papar_cols = [
    "BULAN_TAHUN", "NO_BAUCAR", "NAMA", "ID", "NAMA_ID",
    "NAMA_EMEL", "EMAIL_PEMILIK",
    "STATUS_KEMASKINI", "UMUR_BULAN", "KATEGORI_AGING",
    "DATE", "NO_KOTAK", "KOTAK_TAMBAHAN", "EMAIL"
]
papar_cols = [col for col in papar_cols if col in df_filter.columns]

def multi_search_dataframe(dataframe, search_text, columns):
    """
    Multi carian dalam jadual.
    Pengguna boleh masukkan banyak kata kunci / No Baucar sekaligus
    dengan pemisah koma, titik koma atau baris baharu.

    Contoh:
    60000001, 60000002
    atau paste satu senarai secara menegak.

    Logic carian = OR:
    mana-mana kata kunci yang ditemui pada mana-mana column dipaparkan akan dikekalkan.
    """
    if not search_text or not str(search_text).strip():
        return dataframe.copy()

    import re

    terms = [
        x.strip()
        for x in re.split(r"[,;\n\r]+", str(search_text))
        if x.strip()
    ]

    if not terms:
        return dataframe.copy()

    search_cols = [c for c in columns if c in dataframe.columns]

    if not search_cols:
        return dataframe.copy()

    # Mask keseluruhan: mana-mana keyword jumpa pada mana-mana column = papar row.
    # Kaedah ini sengaja tidak menggunakan DataFrame.agg(" | ".join, axis=1)
    # supaya stabil untuk Timestamp, NaN, nombor dan pandas versi baharu.
    mask = pd.Series(False, index=dataframe.index, dtype=bool)

    for term in terms:
        term_upper = str(term).strip().upper()

        if not term_upper:
            continue

        term_mask = pd.Series(False, index=dataframe.index, dtype=bool)

        for col in search_cols:
            col_text = dataframe[col].fillna("").astype(str).str.upper()
            term_mask = term_mask | col_text.str.contains(
                term_upper,
                regex=False,
                na=False
            )

        mask = mask | term_mask

    return dataframe.loc[mask].copy()


with tab1:
    search_semua = st.text_area(
        "🔎 Carian Multi - Semua Baucar",
        key="search_semua_baucar",
        placeholder="Contoh: 60000001, 60000002\nAtau paste satu senarai No Baucar / Nama / ID / Kotak / Email",
        height=85
    )

    semua_papar = multi_search_dataframe(
        df_filter,
        search_semua,
        papar_cols
    )

    st.caption(f"Paparan: {len(semua_papar):,} daripada {len(df_filter):,} rekod")
    st.dataframe(semua_papar[papar_cols], use_container_width=True, hide_index=True)

with tab2:
    telah = df_filter[df_filter["TELAH_DIKEMASKINI"]].copy()

    search_telah = st.text_area(
        "🔎 Carian Multi - Telah Dikemaskini",
        key="search_telah_dikemaskini",
        placeholder="Contoh: 60000001, 60000002\nAtau paste satu senarai No Baucar / Nama / ID / Kotak / Email",
        height=85
    )

    telah_papar = multi_search_dataframe(
        telah,
        search_telah,
        papar_cols
    )

    st.caption(f"Paparan: {len(telah_papar):,} daripada {len(telah):,} rekod")
    st.dataframe(telah_papar[papar_cols], use_container_width=True, hide_index=True)

with tab3:
    belum = df_filter[df_filter["STATUS_KEMASKINI"] == "BELUM DIKEMASKINI"].copy()

    search_belum = st.text_area(
        "🔎 Carian Multi - Belum Dikemaskini",
        key="search_belum_dikemaskini",
        placeholder="Contoh: 60000001, 60000002\nAtau paste satu senarai No Baucar / Nama / ID",
        height=85
    )

    belum_papar = multi_search_dataframe(
        belum,
        search_belum,
        papar_cols
    )

    st.caption(f"Paparan: {len(belum_papar):,} daripada {len(belum):,} rekod")
    st.dataframe(belum_papar[papar_cols], use_container_width=True, hide_index=True)



with tab4:
    st.markdown("### ⏳ Aging Baucar Belum Dikemaskini")
    st.caption(
        "Aging dikira terus daripada BULAN_TAHUN dalam sheet BAUCAR. "
        "Kategori: 0-3 bulan, 3-6 bulan, 6-9 bulan, 9-12 bulan dan >1 tahun. "
        "Tab ini tidak dipengaruhi filter Tahun/Bulan di sidebar."
    )

    # Aging sengaja menggunakan keseluruhan master data (df), bukan df_filter.
    # Ini memastikan baucar lama 2024/2025 tidak hilang apabila filter Tahun/Bulan
    # pada dashboard utama sedang dipilih.
    # Semua baucar BELUM DIKEMASKINI.
    belum_semua_aging = df[
        df["STATUS_KEMASKINI"] == "BELUM DIKEMASKINI"
    ].copy()

    # Rekod yang berjaya dikira aging.
    aging_base = belum_semua_aging[
        belum_semua_aging["UMUR_BULAN"].notna()
    ].copy()

    # Rekod yang BULAN/TAHUN masih tidak dapat dibaca.
    aging_invalid = belum_semua_aging[
        belum_semua_aging["UMUR_BULAN"].isna()
    ].copy()

    # Carian multi khas aging
    search_aging = st.text_area(
        "🔎 Carian Multi - Aging Baucar",
        key="search_aging_baucar",
        placeholder="Contoh: 60000001, 60000002\\nAtau paste No Baucar / Nama / ID / Email Pemilik",
        height=85
    )

    aging_search_cols = [
        c for c in [
            "NO_BAUCAR", "NAMA", "ID", "NAMA_ID",
            "NAMA_EMEL", "EMAIL_PEMILIK",
            "BULAN_TAHUN", "KATEGORI_AGING"
        ]
        if c in aging_base.columns
    ]

    aging_filtered = multi_search_dataframe(
        aging_base,
        search_aging,
        aging_search_cols
    )

    # Filter kategori aging
    fixed_aging_categories = [
        "0-3 BULAN",
        "3-6 BULAN",
        "6-9 BULAN",
        "9-12 BULAN",
        ">1 TAHUN"
    ]

    aging_categories = [
        c for c in fixed_aging_categories
        if c in aging_filtered["KATEGORI_AGING"].dropna().astype(str).unique().tolist()
    ]

    # Kekalkan >1 TAHUN sebagai pilihan tetap jika ada rekod 12 bulan dan ke atas.
    if (aging_filtered["UMUR_BULAN"] >= 12).any() and ">1 TAHUN" not in aging_categories:
        aging_categories.append(">1 TAHUN")

    aging_category_filter = st.multiselect(
        "Kategori Aging",
        aging_categories,
        default=aging_categories,
        key="aging_category_filter"
    )

    if aging_category_filter:
        aging_filtered = aging_filtered[
            aging_filtered["KATEGORI_AGING"].isin(aging_category_filter)
        ].copy()

    # KPI ringkas
    jumlah_baucar_aging = len(aging_filtered)
    jumlah_pemilik_aging = (
        aging_filtered["ID"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )
    jumlah_email_aging = (
        aging_filtered.loc[
            aging_filtered["EMAIL_PEMILIK"].fillna("").astype(str).str.strip().ne(""),
            "ID"
        ]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    jumlah_lebih_1_tahun = len(
        aging_filtered[aging_filtered["UMUR_BULAN"] >= 12]
    )

    jumlah_aging_invalid = len(aging_invalid)

    jumlah_belum_semua = len(belum_semua_aging)

    ak1, ak2, ak3, ak4, ak5, ak6 = st.columns(6)
    ak1.metric("Belum Dikemaskini", f"{jumlah_belum_semua:,}")
    ak2.metric("Berjaya Dikira Aging", f"{jumlah_baucar_aging:,}")
    ak3.metric("> 1 Tahun", f"{jumlah_lebih_1_tahun:,}")
    ak4.metric("Pemilik / ID", f"{jumlah_pemilik_aging:,}")
    ak5.metric("Pemilik Ada Email", f"{jumlah_email_aging:,}")
    ak6.metric("Tarikh Aging Tidak Sah", f"{jumlah_aging_invalid:,}")

    # Ringkasan aging ikut kategori
    aging_summary = (
        aging_filtered
        .groupby("KATEGORI_AGING", dropna=False)
        .size()
        .reset_index(name="JUMLAH_BAUCAR")
    )

    if not aging_summary.empty:
        aging_summary["_SORT"] = aging_summary["KATEGORI_AGING"].apply(aging_sort_key)
        aging_summary = aging_summary.sort_values("_SORT").drop(columns="_SORT")

        fig_aging = px.bar(
            aging_summary,
            x="KATEGORI_AGING",
            y="JUMLAH_BAUCAR",
            text="JUMLAH_BAUCAR",
            title="Jumlah Baucar Belum Dikemaskini Mengikut Aging"
        )
        fig_aging.update_layout(
            height=380,
            xaxis_title="Kategori Aging",
            yaxis_title="Jumlah Baucar",
            margin=dict(l=30, r=20, t=45, b=60)
        )
        st.plotly_chart(fig_aging, use_container_width=True)

    # Ringkasan per pemilik / ID
    fixed_aging_cols = [
        "0-3 BULAN",
        "3-6 BULAN",
        "6-9 BULAN",
        "9-12 BULAN",
        ">1 TAHUN"
    ]

    # Initialize supaya variable sentiasa wujud walaupun tiada data.
    pivot_aging = pd.DataFrame(
        columns=[
            "ID",
            "NAMA_PEMILIK",
            "EMAIL_PEMILIK"
        ] + fixed_aging_cols + ["JUMLAH"]
    )

    lebih_1_tahun_df = aging_filtered[
        aging_filtered["UMUR_BULAN"] >= 12
    ].copy()

    if not aging_filtered.empty:
        aging_filtered["NAMA_PEMILIK"] = (
            aging_filtered["NAMA_EMEL"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        aging_filtered.loc[
            aging_filtered["NAMA_PEMILIK"] == "",
            "NAMA_PEMILIK"
        ] = (
            aging_filtered["NAMA_ID"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        aging_filtered.loc[
            aging_filtered["NAMA_PEMILIK"] == "",
            "NAMA_PEMILIK"
        ] = (
            aging_filtered["NAMA"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # Elak rekod tercicir apabila nama/email kosong.
        aging_filtered["ID"] = (
            aging_filtered["ID"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        aging_filtered["NAMA_PEMILIK"] = (
            aging_filtered["NAMA_PEMILIK"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        aging_filtered["EMAIL_PEMILIK"] = (
            aging_filtered["EMAIL_PEMILIK"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        aging_filtered.loc[
            aging_filtered["ID"] == "",
            "ID"
        ] = "(Blank)"

        aging_filtered.loc[
            aging_filtered["NAMA_PEMILIK"] == "",
            "NAMA_PEMILIK"
        ] = "(Tiada Nama)"

        aging_filtered.loc[
            aging_filtered["EMAIL_PEMILIK"] == "",
            "EMAIL_PEMILIK"
        ] = "(Tiada Email)"

        pivot_aging = pd.pivot_table(
            aging_filtered,
            index=["ID", "NAMA_PEMILIK", "EMAIL_PEMILIK"],
            columns="KATEGORI_AGING",
            values="NO_BAUCAR",
            aggfunc="count",
            fill_value=0,
            dropna=False
        ).reset_index()

        # Pastikan semua kategori sentiasa ada.
        for col in fixed_aging_cols:
            if col not in pivot_aging.columns:
                pivot_aging[col] = 0

        pivot_aging["JUMLAH"] = (
            pivot_aging[fixed_aging_cols]
            .sum(axis=1)
        )

        pivot_aging = pivot_aging[
            [
                "ID",
                "NAMA_PEMILIK",
                "EMAIL_PEMILIK"
            ]
            + fixed_aging_cols
            + ["JUMLAH"]
        ].sort_values(
            "JUMLAH",
            ascending=False
        )

    # Semakan khusus baucar > 1 tahun
    st.markdown("#### Semakan Baucar > 1 Tahun")

    vt1, vt2 = st.columns(2)

    vt1.metric(
        "Jumlah Baucar > 1 Tahun",
        f"{len(lebih_1_tahun_df):,}"
    )

    jumlah_id_lebih_1_tahun = (
        lebih_1_tahun_df["ID"]
        .fillna("")
        .astype(str)
        .str.strip()
        .replace("", pd.NA)
        .dropna()
        .nunique()
    )

    vt2.metric(
        "Pemilik / ID > 1 Tahun",
        f"{jumlah_id_lebih_1_tahun:,}"
    )

    with st.expander("Lihat senarai baucar > 1 tahun"):
        lebih_1_tahun_cols = [
            c for c in [
                "BULAN_TAHUN",
                "NO_BAUCAR",
                "ID",
                "NAMA",
                "NAMA_EMEL",
                "EMAIL_PEMILIK",
                "UMUR_BULAN",
                "KATEGORI_AGING",
                "STATUS_KEMASKINI"
            ]
            if c in lebih_1_tahun_df.columns
        ]

        if lebih_1_tahun_df.empty:
            st.info("Tiada baucar > 1 tahun untuk pilihan semasa.")
        else:
            st.dataframe(
                lebih_1_tahun_df[
                    lebih_1_tahun_cols
                ].sort_values(
                    ["UMUR_BULAN", "ID"],
                    ascending=[False, True]
                ),
                use_container_width=True,
                hide_index=True
            )

    st.markdown("#### Ringkasan Aging Mengikut Pemilik / ID")

    if pivot_aging.empty:
        st.info("Tiada rekod aging untuk pilihan semasa.")
    else:
        st.dataframe(
            pivot_aging,
            use_container_width=True,
            hide_index=True
        )

    if not aging_invalid.empty:
        with st.expander("⚠️ Lihat rekod yang BULAN/TAHUN tidak dapat dikira"):
            invalid_cols = [
                c for c in [
                    "BULAN_TAHUN", "AGING_MONTH_NUM", "AGING_YEAR_NUM", "NO_BAUCAR", "ID", "NAMA",
                    "NAMA_EMEL", "EMAIL_PEMILIK", "STATUS_KEMASKINI"
                ]
                if c in aging_invalid.columns
            ]
            st.dataframe(
                aging_invalid[invalid_cols],
                use_container_width=True,
                hide_index=True
            )

    # Detail semua baucar aging
    st.markdown("#### Senarai Detail Baucar Aging")

    aging_detail_cols = [
        c for c in [
            "BULAN_TAHUN",
            "NO_BAUCAR",
            "ID",
            "NAMA",
            "NAMA_EMEL",
            "EMAIL_PEMILIK",
            "UMUR_BULAN",
            "KATEGORI_AGING",
            "STATUS_KEMASKINI"
        ]
        if c in aging_filtered.columns
    ]

    # Debug / sanity check ringkas mengikut tahun sumber BAUCAR
    aging_year_check = (
        aging_filtered
        .groupby("TAHUN", dropna=False)
        .size()
        .reset_index(name="JUMLAH_BELUM_DIKEMASKINI_AGING")
        .sort_values("TAHUN")
    )

    with st.expander("Semakan aging mengikut tahun BAUCAR"):
        st.dataframe(
            aging_year_check,
            use_container_width=True,
            hide_index=True
        )

    st.caption(f"Paparan: {len(aging_filtered):,} rekod aging")
    st.dataframe(
        aging_filtered[aging_detail_cols].sort_values(
            ["UMUR_BULAN", "ID"],
            ascending=[False, True]
        ),
        use_container_width=True,
        hide_index=True
    )


st.markdown("### 📧 Semakan Padanan Email Pemilik")

email_check = df[["ID", "NAMA_ID", "NAMA_EMEL", "EMAIL_PEMILIK"]].drop_duplicates().copy()
email_check["ADA_EMAIL"] = email_check["EMAIL_PEMILIK"].fillna("").astype(str).str.strip().ne("")

jumlah_id = email_check["ID"].fillna("").astype(str).str.strip().replace("", pd.NA).dropna().nunique()
jumlah_ada_email = email_check[email_check["ADA_EMAIL"]]["ID"].fillna("").astype(str).str.strip().replace("", pd.NA).dropna().nunique()
jumlah_tiada_email = max(jumlah_id - jumlah_ada_email, 0)

ec1, ec2, ec3 = st.columns(3)
ec1.metric("Jumlah ID", f"{jumlah_id:,}")
ec2.metric("ID Ada Email", f"{jumlah_ada_email:,}")
ec3.metric("ID Tiada Email", f"{jumlah_tiada_email:,}")

with st.expander("Lihat ID yang belum mempunyai email"):
    missing_email_df = email_check[~email_check["ADA_EMAIL"]].copy()
    st.dataframe(
        missing_email_df[["ID", "NAMA_ID", "NAMA_EMEL"]],
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

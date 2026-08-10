import os
import re
import sys
import time
from io import StringIO
import pandas as pd
import requests

BAUCAR_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1370653594&single=true&output=csv"
APPLIKASI_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1571972700&single=true&output=csv"
EMEL_CSV_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/pub?gid=1298317374&single=true&output=csv"

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"

SCRIPT_VERSION = "BKA-BREVO-2026-08-10-V3-UNDERSCORE"
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "").strip()
BREVO_FROM_EMAIL = os.getenv("BREVO_FROM_EMAIL", "").strip()
BREVO_FROM_NAME = os.getenv("BREVO_FROM_NAME", "E-Filing BKA").strip()
TEST_MODE = os.getenv("TEST_MODE", "true").strip().lower() == "true"
TEST_EMAIL = os.getenv("TEST_EMAIL", "").strip()
GROUP_KEWANGAN_EMAIL = os.getenv("GROUP_KEWANGAN_EMAIL", "").strip()
TEST_MAX_EMAILS = int(os.getenv("TEST_MAX_EMAILS", "3"))


def load_csv_url(url, label="CSV"):
    """
    Load published Google Sheet CSV using requests instead of pandas URL opener.
    More stable in GitHub Actions because Google may redirect the published URL.
    """
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/csv,text/plain,*/*",
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=90,
        allow_redirects=True,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Gagal baca {label}: HTTP {response.status_code} | "
            f"URL akhir: {response.url} | "
            f"Response: {response.text[:300]}"
        )

    content = response.text

    if not content.strip():
        raise RuntimeError(f"{label} kosong.")

    return pd.read_csv(
        StringIO(content),
        dtype=str
    )

def validate_config():
    missing = []
    if not BREVO_API_KEY:
        missing.append("BREVO_API_KEY")
    if not BREVO_FROM_EMAIL:
        missing.append("BREVO_FROM_EMAIL")
    if TEST_MODE and not TEST_EMAIL:
        missing.append("TEST_EMAIL")
    if missing:
        raise ValueError("GitHub Secret belum lengkap: " + ", ".join(missing))

def clean_text(series):
    return series.fillna("").astype(str).str.strip()

def clean_id(series):
    return series.fillna("").astype(str).str.strip().str.replace(r"\.0$", "", regex=True)

def clean_no_baucar(series):
    cleaned = (
        series.fillna("").astype(str).str.strip().str.upper()
        .str.replace(r"\.0$", "", regex=True)
        .str.replace(r"[^A-Z0-9]", "", regex=True)
    )
    return cleaned.apply(lambda x: str(int(x)) if isinstance(x, str) and x.isdigit() and x else x)

def normalize_status(series):
    return series.fillna("").astype(str).str.upper().str.strip().str.replace(r"\s+", "", regex=True)

def extract_month_year(value):
    """
    Parse BULAN_TAHUN kepada (tahun, bulan).

    Format sebenar BAUCAR:
        Jan_2024
        Feb_2024
        Mar_2024
        ...
        Aug_2026

    Juga support separator space, dash dan slash.
    """

    if pd.isna(value):
        return None, None

    raw = str(value).strip()

    if not raw:
        return None, None

    s = raw.upper().strip()

    month_map = {
        "JAN": 1,
        "FEB": 2,
        "MAR": 3,
        "MAC": 3,
        "APR": 4,
        "MAY": 5,
        "MEI": 5,
        "JUN": 6,
        "JUL": 7,
        "AUG": 8,
        "OGO": 8,
        "OGOS": 8,
        "SEP": 9,
        "SEPT": 9,
        "OCT": 10,
        "OKT": 10,
        "NOV": 11,
        "DEC": 12,
        "DIS": 12,
    }

    # PRIORITY 1:
    # Format sebenar: Jan_2024 / Jan-2024 / Jan 2024 / Jan/2024
    m = re.match(
        r"^([A-Z]+)[_\s\-/]+(20\d{2})$",
        s
    )

    if m:
        month_token = m.group(1)
        year = int(m.group(2))
        month = month_map.get(month_token)

        if month is not None:
            return year, month

    # PRIORITY 2:
    # MM_YYYY / MM-YYYY / MM/YYYY
    m = re.match(
        r"^(0?[1-9]|1[0-2])[_\s\-/]+(20\d{2})$",
        s
    )

    if m:
        return int(m.group(2)), int(m.group(1))

    # PRIORITY 3:
    # YYYY_MM / YYYY-MM / YYYY/MM
    m = re.match(
        r"^(20\d{2})[_\s\-/]+(0?[1-9]|1[0-2])$",
        s
    )

    if m:
        return int(m.group(1)), int(m.group(2))

    # PRIORITY 4:
    # Find month token + year anywhere in string
    year_match = re.search(r"(20\d{2})", s)
    if year_match:
        year = int(year_match.group(1))

        for token, month in month_map.items():
            if token in s:
                return year, month

    # Last fallback
    normalized = re.sub(r"[_]+", " ", raw)

    try:
        dt = pd.to_datetime(
            normalized,
            errors="coerce",
            dayfirst=True
        )

        if not pd.isna(dt):
            return int(dt.year), int(dt.month)

    except Exception:
        pass

    return None, None

def calculate_age_months(value, reference_date=None):
    if reference_date is None:
        reference_date = pd.Timestamp.today().normalize()

    year, month = extract_month_year(value)

    if year is None or month is None:
        return None

    return (reference_date.year - year) * 12 + (reference_date.month - month)


def aging_category(age):
    if age is None or pd.isna(age):
        return "TIDAK SAH"

    age = int(age)

    if age < 3:
        return "0-3 BULAN"
    if age < 6:
        return "3-6 BULAN"
    if age < 9:
        return "6-9 BULAN"
    if age < 12:
        return "9-12 BULAN"

    return ">1 TAHUN"


def print_aging_debug(df):
    print("")
    print("========== DEBUG AGING ==========")

    sample = (
        df[["BULAN_TAHUN", "UMUR_BULAN", "KATEGORI_AGING"]]
        .drop_duplicates()
        .head(20)
    )

    print("Contoh BULAN_TAHUN -> UMUR_BULAN:")
    for _, row in sample.iterrows():
        print(
            f"{repr(row['BULAN_TAHUN'])} -> "
            f"{row['UMUR_BULAN']} -> "
            f"{row['KATEGORI_AGING']}"
        )

    invalid = df[df["UMUR_BULAN"].isna()].copy()

    print(f"Jumlah aging tidak sah: {len(invalid):,}")

    if not invalid.empty:
        print("Contoh BULAN_TAHUN gagal parse:")
        for value in (
            invalid["BULAN_TAHUN"]
            .fillna("")
            .astype(str)
            .drop_duplicates()
            .head(20)
            .tolist()
        ):
            print(f"- {repr(value)}")

    print("=================================")
    print("")

def normalize_email_sheet(emel):
    cmap = {str(c).strip().upper(): c for c in emel.columns}
    id_col = next((cmap[x] for x in ["ID","NO STAF","NO STAFF"] if x in cmap), None)
    name_col = next((cmap[x] for x in ["NAMA","NAME"] if x in cmap), None)
    email_col = next((cmap[x] for x in ["EMAIL","E-MAIL","EMEL"] if x in cmap), None)
    if id_col is None or email_col is None:
        response = requests.get(
            EMEL_CSV_URL,
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=90,
            allow_redirects=True,
        )
        if response.status_code != 200:
            raise RuntimeError(
                f"Gagal baca EMEL tanpa header: HTTP {response.status_code}"
            )
        emel = pd.read_csv(
            StringIO(response.text),
            dtype=str,
            header=None
        ).iloc[:, :3].copy()
        emel.columns = ["ID","NAMA_EMEL","EMAIL_PEMILIK"]
    else:
        rename_map = {id_col:"ID", email_col:"EMAIL_PEMILIK"}
        if name_col is not None:
            rename_map[name_col] = "NAMA_EMEL"
        emel = emel.rename(columns=rename_map)
        if "NAMA_EMEL" not in emel.columns:
            emel["NAMA_EMEL"] = ""
    emel["ID"] = clean_id(emel["ID"])
    emel["NAMA_EMEL"] = clean_text(emel["NAMA_EMEL"])
    emel["EMAIL_PEMILIK"] = clean_text(emel["EMAIL_PEMILIK"]).str.lower()
    emel = emel[(emel["ID"] != "") & (emel["ID"].str.upper() != "ID") & (emel["EMAIL_PEMILIK"].str.upper() != "EMAIL")].copy()
    return emel.drop_duplicates(subset=["ID"], keep="first")

def build_master_data():
    baucar = load_csv_url(BAUCAR_CSV_URL, "BAUCAR")
    aplikasi = load_csv_url(APPLIKASI_CSV_URL, "APPLIKASI")
    emel = load_csv_url(EMEL_CSV_URL, "EMEL")
    for df in (baucar, aplikasi, emel):
        df.columns = df.columns.astype(str).str.strip()

    baucar = baucar.rename(columns={"BULAN/TAHUN":"BULAN_TAHUN","NO BAUCAR":"NO_BAUCAR","Name":"NAMA","NAME":"NAMA","ID":"ID"})
    aplikasi = aplikasi.rename(columns={"TIMESTAMP":"DATE","DATE":"DATE","IN / OUT":"IN_OUT","IN/OUT":"IN_OUT","IN OUT":"IN_OUT","NO BAUCAR":"NO_BAUCAR","NO. BAUCAR":"NO_BAUCAR"})

    for c in ["BULAN_TAHUN","NO_BAUCAR","NAMA","ID"]:
        if c not in baucar.columns:
            raise ValueError(f"Column BAUCAR tidak dijumpai: {c}")
    for c in ["NO_BAUCAR","IN_OUT"]:
        if c not in aplikasi.columns:
            raise ValueError(f"Column APPLIKASI tidak dijumpai: {c}")

    baucar["ID"] = clean_id(baucar["ID"])
    baucar["NO_BAUCAR_CLEAN"] = clean_no_baucar(baucar["NO_BAUCAR"])

    aplikasi["NO_BAUCAR_LIST"] = aplikasi["NO_BAUCAR"].fillna("").astype(str).str.split(",")
    aplikasi = aplikasi.explode("NO_BAUCAR_LIST").copy()
    aplikasi["NO_BAUCAR"] = aplikasi["NO_BAUCAR_LIST"]
    aplikasi["NO_BAUCAR_CLEAN"] = clean_no_baucar(aplikasi["NO_BAUCAR"])
    aplikasi = aplikasi[(aplikasi["NO_BAUCAR_CLEAN"] != "") & (aplikasi["NO_BAUCAR_CLEAN"] != "LOADING")].copy()
    aplikasi["IN_OUT"] = normalize_status(aplikasi["IN_OUT"])
    aplikasi.loc[~aplikasi["IN_OUT"].isin(["IN","OUT"]), "IN_OUT"] = ""
    aplikasi["_ROW_ORDER"] = range(len(aplikasi))

    latest_status = (
        aplikasi[aplikasi["IN_OUT"].isin(["IN","OUT"])]
        .sort_values("_ROW_ORDER")
        .drop_duplicates(subset=["NO_BAUCAR_CLEAN"], keep="last")
    )

    df = baucar.copy()
    if latest_status.empty:
        df["IN_OUT"] = ""
    else:
        df = df.merge(latest_status[["NO_BAUCAR_CLEAN","IN_OUT"]], on="NO_BAUCAR_CLEAN", how="left")

    df["STATUS_KEMASKINI"] = "BELUM DIKEMASKINI"
    df.loc[df["IN_OUT"] == "IN", "STATUS_KEMASKINI"] = "IN"
    df.loc[df["IN_OUT"] == "OUT", "STATUS_KEMASKINI"] = "OUT"

    emel = normalize_email_sheet(emel)
    df = df.merge(emel[["ID","NAMA_EMEL","EMAIL_PEMILIK"]], on="ID", how="left")
    df["UMUR_BULAN"] = df["BULAN_TAHUN"].apply(calculate_age_months)
    df["KATEGORI_AGING"] = df["UMUR_BULAN"].apply(aging_category)
    return df

def safe_html(value):
    s = "" if pd.isna(value) else str(value)
    return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def first_non_blank(series, fallback=""):
    vals = series.fillna("").astype(str).str.strip()
    vals = vals[vals != ""]
    return vals.iloc[0] if not vals.empty else fallback

def build_email_html(owner_name, owner_id, rows):
    cats = ["3-6 BULAN","6-9 BULAN","9-12 BULAN",">1 TAHUN"]
    counts = {c:int((rows["KATEGORI_AGING"] == c).sum()) for c in cats}
    detail = []
    for _, row in rows.sort_values(["UMUR_BULAN","NO_BAUCAR"], ascending=[False,True]).iterrows():
        age = "" if pd.isna(row["UMUR_BULAN"]) else str(int(row["UMUR_BULAN"]))
        detail.append(f"""
        <tr>
          <td style="padding:8px;border:1px solid #ddd;">{safe_html(row.get("NO_BAUCAR",""))}</td>
          <td style="padding:8px;border:1px solid #ddd;">{safe_html(row.get("BULAN_TAHUN",""))}</td>
          <td style="padding:8px;border:1px solid #ddd;text-align:center;">{safe_html(age)}</td>
          <td style="padding:8px;border:1px solid #ddd;">{safe_html(row.get("KATEGORI_AGING",""))}</td>
        </tr>""")
    return f"""
    <html><body style="font-family:Arial,sans-serif;color:#222;">
    <h2>E-Filing BKA</h2>
    <p>Tuan/Puan <b>{safe_html(owner_name)}</b>,</p>
    <p>Berdasarkan rekod E-Filing BKA, terdapat <b>{len(rows):,} baucar</b> di bawah ID <b>{safe_html(owner_id)}</b> yang masih belum dikemaskini dan telah mencapai tempoh tiga (3) bulan atau lebih.</p>

    <h3>Ringkasan Aging</h3>
    <table style="border-collapse:collapse;width:520px;">
      <tr><th style="padding:8px;border:1px solid #ddd;text-align:left;">Kategori</th><th style="padding:8px;border:1px solid #ddd;text-align:right;">Jumlah</th></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;">3-6 Bulan</td><td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts["3-6 BULAN"]:,}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;">6-9 Bulan</td><td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts["6-9 BULAN"]:,}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;">9-12 Bulan</td><td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts["9-12 BULAN"]:,}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;">&gt; 1 Tahun</td><td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts[">1 TAHUN"]:,}</td></tr>
      <tr><td style="padding:8px;border:1px solid #ddd;"><b>Jumlah</b></td><td style="padding:8px;border:1px solid #ddd;text-align:right;"><b>{len(rows):,}</b></td></tr>
    </table>

    <h3>Senarai Baucar</h3>
    <table style="border-collapse:collapse;width:100%;">
      <tr><th style="padding:8px;border:1px solid #ddd;">No. Baucar</th><th style="padding:8px;border:1px solid #ddd;">Bulan/Tahun</th><th style="padding:8px;border:1px solid #ddd;">Umur (Bulan)</th><th style="padding:8px;border:1px solid #ddd;">Aging</th></tr>
      {''.join(detail)}
    </table>

    <p>Mohon semakan dan tindakan kemaskini dibuat dalam E-Filing BKA.</p>
    <p>Sekian, terima kasih.</p>
    <p><b>Bahagian Kewangan & Akaun</b><br>CIDB Malaysia</p>
    <hr>
    <p style="font-size:11px;color:#777;">Email ini dijana secara automatik oleh sistem E-Filing BKA.</p>
    </body></html>
    """

def send_brevo_email(to_email, to_name, subject, html_body, cc_email=""):
    headers = {"accept":"application/json","content-type":"application/json","api-key":BREVO_API_KEY}
    payload = {
        "sender":{"name":BREVO_FROM_NAME,"email":BREVO_FROM_EMAIL},
        "to":[{"email":to_email,"name":to_name}],
        "subject":subject,
        "htmlContent":html_body,
    }
    if cc_email:
        payload["cc"] = [{"email":cc_email,"name":"Group Kewangan"}]
    response = requests.post(BREVO_API_URL, headers=headers, json=payload, timeout=60)
    if response.status_code not in (200,201,202):
        raise RuntimeError(f"Brevo API error {response.status_code}: {response.text}")
    return response.json() if response.text else {}

def main():
    validate_config()
    print("E-FILING BKA - BREVO EMAIL REMINDER")
    print(f"SCRIPT_VERSION={SCRIPT_VERSION}")
    print(f"TEST_MODE={TEST_MODE}")
    print("========== SELF TEST PARSER ==========")
    for test_value in ["Jan_2024", "Aug_2025", "Jul_2026"]:
        test_year, test_month = extract_month_year(test_value)
        test_age = calculate_age_months(test_value)
        print(
            f"{test_value} -> year={test_year}, month={test_month}, age={test_age}"
        )
    print("======================================")
    print("")

    df = build_master_data()

    print_aging_debug(df)

    belum = df[df["STATUS_KEMASKINI"] == "BELUM DIKEMASKINI"].copy()
    reminder = belum[(belum["UMUR_BULAN"].notna()) & (belum["UMUR_BULAN"] >= 3)].copy()

    print(f"Jumlah master BAUCAR: {len(df):,}")
    print(f"Jumlah BELUM DIKEMASKINI: {len(belum):,}")
    print(f"Jumlah reminder >=3 bulan: {len(reminder):,}")

    if reminder.empty:
        print("Tiada baucar reminder >=3 bulan. Semak DEBUG AGING di atas.")
        sys.exit(1)

    sent = skipped = failed = 0
    grouped = reminder.groupby("ID", dropna=False)

    for owner_id, rows in grouped:
        owner_id = str(owner_id).strip()
        owner_name = first_non_blank(rows["NAMA_EMEL"], first_non_blank(rows["NAMA"], owner_id))
        owner_email = first_non_blank(rows["EMAIL_PEMILIK"], "")

        if not owner_email:
            print(f"SKIP ID {owner_id}: tiada email.")
            skipped += 1
            continue

        actual_to = TEST_EMAIL if TEST_MODE else owner_email
        actual_name = f"TEST - {owner_name}" if TEST_MODE else owner_name
        actual_cc = "" if TEST_MODE else GROUP_KEWANGAN_EMAIL

        subject = f"Peringatan Mingguan E-Filing BKA - {len(rows):,} Baucar Belum Dikemaskini"
        html = build_email_html(owner_name, owner_id, rows)

        if TEST_MODE:
            banner = f"""<div style="background:#fff3cd;border:1px solid #ffe69c;padding:12px;margin-bottom:15px;font-family:Arial;">
            <b>TEST MODE</b><br>
            Pemilik sebenar: {safe_html(owner_name)}<br>
            ID sebenar: {safe_html(owner_id)}<br>
            Email sebenar: {safe_html(owner_email)}<br>
            Jumlah baucar: {len(rows):,}
            </div>"""
            html = banner + html

        try:
            result = send_brevo_email(actual_to, actual_name, subject, html, actual_cc)
            print(f"SENT | ID={owner_id} | TO={actual_to} | BAUCAR={len(rows):,} | MESSAGE_ID={result.get('messageId','')}")
            sent += 1
        except Exception as exc:
            print(f"FAILED | ID={owner_id} | {exc}")
            failed += 1

        time.sleep(0.2)

        if TEST_MODE and sent >= TEST_MAX_EMAILS:
            print("TEST limit dicapai. Stop penghantaran.")
            break

    print(f"Berjaya dihantar: {sent}")
    print(f"Tiada email: {skipped}")
    print(f"Gagal: {failed}")

    if failed:
        sys.exit(1)

if __name__ == "__main__":
    main()

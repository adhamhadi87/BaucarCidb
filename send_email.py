import os
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import pandas as pd


# ==========================================================
# CONFIG
# ==========================================================

BAUCAR_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/"
    "pub?gid=1370653594&single=true&output=csv"
)

APPLIKASI_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/"
    "pub?gid=1571972700&single=true&output=csv"
)

EMEL_CSV_URL = (
    "https://docs.google.com/spreadsheets/d/e/"
    "2PACX-1vTZIvd34YjLZRE_05LPX8tPH5bS20MWU_UnBQ9-Z_nep20bk4t0bdw8kdX2RKZyNfi1veTDyfcH3ZS9/"
    "pub?gid=1298317374&single=true&output=csv"
)

# Semua credential akan dibaca daripada GitHub Secrets / environment variables.
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USERNAME)
GROUP_KEWANGAN_EMAIL = os.getenv("GROUP_KEWANGAN_EMAIL", "")

# TEST_MODE = true bermaksud semua email pergi ke TEST_EMAIL sahaja.
TEST_MODE = os.getenv("TEST_MODE", "true").strip().lower() == "true"
TEST_EMAIL = os.getenv("TEST_EMAIL", "")


# ==========================================================
# HELPER
# ==========================================================

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
        lambda x: str(int(x))
        if isinstance(x, str) and x.isdigit() and x != ""
        else x
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


def extract_month_year(value):
    """
    Parse BULAN_TAHUN kepada (tahun, bulan).
    Sokong:
    JAN 2026
    JAN/2026
    01/2026
    2026-01
    dan format tarikh biasa.
    """
    if pd.isna(value):
        return None, None

    s = str(value).strip()
    if not s:
        return None, None

    upper = s.upper()

    month_map = {
        "JAN": 1, "JANUARI": 1, "JANUARY": 1,
        "FEB": 2, "FEBRUARI": 2, "FEBRUARY": 2,
        "MAC": 3, "MAR": 3, "MARCH": 3,
        "APR": 4, "APRIL": 4,
        "MEI": 5, "MAY": 5,
        "JUN": 6, "JUNE": 6,
        "JUL": 7, "JULY": 7,
        "OGO": 8, "OGOS": 8, "AUG": 8, "AUGUST": 8,
        "SEP": 9, "SEPT": 9, "SEPTEMBER": 9,
        "OKT": 10, "OCT": 10, "OCTOBER": 10,
        "NOV": 11, "NOVEMBER": 11,
        "DIS": 12, "DEC": 12, "DECEMBER": 12,
    }

    year_match = re.search(r"(20\d{2})", upper)
    year = int(year_match.group(1)) if year_match else None

    for key, month_num in month_map.items():
        if re.search(rf"\b{re.escape(key)}\b", upper):
            return year, month_num

    m = re.search(r"(?<!\d)(0?[1-9]|1[0-2])\s*[/-]\s*(20\d{2})(?!\d)", upper)
    if m:
        return int(m.group(2)), int(m.group(1))

    m = re.search(r"(?<!\d)(20\d{2})\s*[/-]\s*(0?[1-9]|1[0-2])(?!\d)", upper)
    if m:
        return int(m.group(1)), int(m.group(2))

    dt = pd.to_datetime(s, errors="coerce", dayfirst=True)
    if not pd.isna(dt):
        return int(dt.year), int(dt.month)

    return None, None


def calculate_age_months(value, reference_date=None):
    if reference_date is None:
        reference_date = pd.Timestamp.today().normalize()

    year, month = extract_month_year(value)

    if year is None or month is None:
        return None

    return (
        (reference_date.year - year) * 12
        + (reference_date.month - month)
    )


def aging_category(age_months):
    if age_months is None or pd.isna(age_months):
        return "TIDAK SAH"

    age_months = int(age_months)

    if age_months < 3:
        return "0-3 BULAN"
    if age_months < 6:
        return "3-6 BULAN"
    if age_months < 9:
        return "6-9 BULAN"
    if age_months < 12:
        return "9-12 BULAN"

    return ">1 TAHUN"


# ==========================================================
# LOAD DATA
# ==========================================================

def load_data():
    baucar = pd.read_csv(BAUCAR_CSV_URL, dtype=str)
    aplikasi = pd.read_csv(APPLIKASI_CSV_URL, dtype=str)
    emel = pd.read_csv(EMEL_CSV_URL, dtype=str)

    baucar.columns = baucar.columns.astype(str).str.strip()
    aplikasi.columns = aplikasi.columns.astype(str).str.strip()
    emel.columns = emel.columns.astype(str).str.strip()

    baucar = baucar.rename(columns={
        "BULAN/TAHUN": "BULAN_TAHUN",
        "NO BAUCAR": "NO_BAUCAR",
        "Name": "NAMA",
        "ID": "ID",
    })

    aplikasi = aplikasi.rename(columns={
        "TIMESTAMP": "DATE",
        "DATE": "DATE",
        "IN / OUT": "IN_OUT",
        "IN/OUT": "IN_OUT",
        "IN OUT": "IN_OUT",
        "NO BAUCAR": "NO_BAUCAR",
        "NO. BAUCAR": "NO_BAUCAR",
    })

    # Normalize email sheet
    emel_map = {str(c).strip().upper(): c for c in emel.columns}

    id_col = next(
        (emel_map[x] for x in ["ID", "NO STAF", "NO STAFF"] if x in emel_map),
        None
    )

    name_col = next(
        (emel_map[x] for x in ["NAMA", "NAME"] if x in emel_map),
        None
    )

    email_col = next(
        (emel_map[x] for x in ["EMAIL", "E-MAIL", "EMEL"] if x in emel_map),
        None
    )

    # Jika sheet emel tiada header
    if id_col is None or email_col is None:
        emel = pd.read_csv(EMEL_CSV_URL, dtype=str, header=None)
        emel = emel.iloc[:, :3].copy()
        emel.columns = ["ID", "NAMA_EMEL", "EMAIL_PEMILIK"]
    else:
        rename_map = {
            id_col: "ID",
            email_col: "EMAIL_PEMILIK",
        }

        if name_col is not None:
            rename_map[name_col] = "NAMA_EMEL"

        emel = emel.rename(columns=rename_map)

        if "NAMA_EMEL" not in emel.columns:
            emel["NAMA_EMEL"] = ""

    return baucar, aplikasi, emel


# ==========================================================
# BUILD MASTER
# Logic sama seperti Streamlit:
# IN / OUT = status terakhir sah dalam APPLIKASI
# BELUM DIKEMASKINI = tiada status sah IN / OUT
# ==========================================================

def build_master():
    baucar, aplikasi, emel = load_data()

    required_baucar = ["BULAN_TAHUN", "NO_BAUCAR", "NAMA", "ID"]
    required_app = ["NO_BAUCAR", "IN_OUT"]

    for col in required_baucar:
        if col not in baucar.columns:
            raise ValueError(f"Column BAUCAR tidak dijumpai: {col}")

    for col in required_app:
        if col not in aplikasi.columns:
            raise ValueError(f"Column APPLIKASI tidak dijumpai: {col}")

    baucar["ID"] = clean_text(baucar["ID"]).str.replace(r"\.0$", "", regex=True)
    baucar["NO_BAUCAR_CLEAN"] = clean_no_baucar(baucar["NO_BAUCAR"])

    aplikasi["NO_BAUCAR_RAW"] = aplikasi["NO_BAUCAR"].fillna("").astype(str)
    aplikasi["NO_BAUCAR_LIST"] = aplikasi["NO_BAUCAR_RAW"].str.split(",")
    aplikasi = aplikasi.explode("NO_BAUCAR_LIST").copy()

    aplikasi["NO_BAUCAR"] = aplikasi["NO_BAUCAR_LIST"]
    aplikasi["NO_BAUCAR_CLEAN"] = clean_no_baucar(aplikasi["NO_BAUCAR"])

    aplikasi = aplikasi[
        (aplikasi["NO_BAUCAR_CLEAN"] != "")
        & (aplikasi["NO_BAUCAR_CLEAN"] != "LOADING")
    ].copy()

    aplikasi["IN_OUT"] = normalize_status(aplikasi["IN_OUT"])
    aplikasi.loc[
        ~aplikasi["IN_OUT"].isin(["IN", "OUT"]),
        "IN_OUT"
    ] = ""

    aplikasi["_ROW_ORDER"] = range(len(aplikasi))

    valid_status_app = aplikasi[
        aplikasi["IN_OUT"].isin(["IN", "OUT"])
    ].copy()

    latest_status = (
        valid_status_app
        .sort_values("_ROW_ORDER")
        .drop_duplicates(
            subset=["NO_BAUCAR_CLEAN"],
            keep="last"
        )
    )

    df = baucar.copy()

    if latest_status.empty:
        df["IN_OUT"] = ""
    else:
        df = df.merge(
            latest_status[
                ["NO_BAUCAR_CLEAN", "IN_OUT"]
            ],
            on="NO_BAUCAR_CLEAN",
            how="left"
        )

    df["STATUS_KEMASKINI"] = "BELUM DIKEMASKINI"

    df.loc[
        df["IN_OUT"] == "IN",
        "STATUS_KEMASKINI"
    ] = "IN"

    df.loc[
        df["IN_OUT"] == "OUT",
        "STATUS_KEMASKINI"
    ] = "OUT"

    # Email lookup
    emel["ID"] = clean_text(emel["ID"]).str.replace(r"\.0$", "", regex=True)
    emel["NAMA_EMEL"] = clean_text(emel["NAMA_EMEL"])
    emel["EMAIL_PEMILIK"] = clean_text(emel["EMAIL_PEMILIK"]).str.lower()

    emel = emel[
        (emel["ID"] != "")
        & (emel["ID"].str.upper() != "ID")
        & (emel["EMAIL_PEMILIK"].str.upper() != "EMAIL")
    ].copy()

    emel = emel.drop_duplicates(
        subset=["ID"],
        keep="first"
    )

    df = df.merge(
        emel[
            ["ID", "NAMA_EMEL", "EMAIL_PEMILIK"]
        ],
        on="ID",
        how="left"
    )

    # Aging
    df["UMUR_BULAN"] = df["BULAN_TAHUN"].apply(
        calculate_age_months
    )

    df["KATEGORI_AGING"] = df["UMUR_BULAN"].apply(
        aging_category
    )

    return df


# ==========================================================
# EMAIL CONTENT
# ==========================================================

def build_email_html(owner_name, owner_id, rows):
    counts = {
        "3-6 BULAN": 0,
        "6-9 BULAN": 0,
        "9-12 BULAN": 0,
        ">1 TAHUN": 0,
    }

    for category, count in rows["KATEGORI_AGING"].value_counts().items():
        if category in counts:
            counts[category] = int(count)

    total = len(rows)

    detail_rows = ""

    for _, row in rows.sort_values(
        ["UMUR_BULAN", "NO_BAUCAR"],
        ascending=[False, True]
    ).iterrows():

        detail_rows += f"""
        <tr>
            <td style="padding:8px;border:1px solid #ddd;">{row.get("NO_BAUCAR", "")}</td>
            <td style="padding:8px;border:1px solid #ddd;">{row.get("BULAN_TAHUN", "")}</td>
            <td style="padding:8px;border:1px solid #ddd;">{int(row.get("UMUR_BULAN", 0)) if pd.notna(row.get("UMUR_BULAN")) else ""}</td>
            <td style="padding:8px;border:1px solid #ddd;">{row.get("KATEGORI_AGING", "")}</td>
        </tr>
        """

    html = f"""
    <html>
    <body style="font-family:Arial,Helvetica,sans-serif;color:#222;">
        <p>Tuan/Puan <b>{owner_name}</b>,</p>

        <p>
            Berdasarkan rekod <b>E-Filing BKA</b>, terdapat
            <b>{total:,} baucar</b> di bawah ID <b>{owner_id}</b>
            yang masih belum dikemaskini dan telah melebihi tempoh tiga (3) bulan.
        </p>

        <h3>Ringkasan Aging</h3>

        <table style="border-collapse:collapse;width:520px;">
            <tr>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Kategori</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:right;">Jumlah</th>
            </tr>
            <tr>
                <td style="padding:8px;border:1px solid #ddd;">3-6 Bulan</td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts["3-6 BULAN"]:,}</td>
            </tr>
            <tr>
                <td style="padding:8px;border:1px solid #ddd;">6-9 Bulan</td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts["6-9 BULAN"]:,}</td>
            </tr>
            <tr>
                <td style="padding:8px;border:1px solid #ddd;">9-12 Bulan</td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts["9-12 BULAN"]:,}</td>
            </tr>
            <tr>
                <td style="padding:8px;border:1px solid #ddd;">&gt; 1 Tahun</td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;">{counts[">1 TAHUN"]:,}</td>
            </tr>
            <tr>
                <td style="padding:8px;border:1px solid #ddd;"><b>Jumlah</b></td>
                <td style="padding:8px;border:1px solid #ddd;text-align:right;"><b>{total:,}</b></td>
            </tr>
        </table>

        <br>

        <h3>Senarai Baucar</h3>

        <table style="border-collapse:collapse;width:100%;">
            <tr>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">No. Baucar</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Bulan/Tahun</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Umur (Bulan)</th>
                <th style="padding:8px;border:1px solid #ddd;text-align:left;">Aging</th>
            </tr>
            {detail_rows}
        </table>

        <p>
            Mohon semakan dan tindakan kemaskini dibuat dalam E-Filing BKA.
        </p>

        <p>
            Sekian, terima kasih.
        </p>

        <p>
            <b>Bahagian Kewangan & Akaun</b><br>
            CIDB Malaysia
        </p>

        <hr>
        <p style="font-size:11px;color:#777;">
            Email ini dijana secara automatik oleh sistem E-Filing BKA.
        </p>
    </body>
    </html>
    """

    return html


# ==========================================================
# SEND EMAIL
# ==========================================================

def send_one_email(to_email, cc_email, subject, html_body):
    msg = MIMEMultipart("alternative")

    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email

    recipients = [to_email]

    if cc_email:
        msg["Cc"] = cc_email
        recipients.append(cc_email)

    msg.attach(
        MIMEText(
            html_body,
            "html",
            "utf-8"
        )
    )

    with smtplib.SMTP(
        SMTP_HOST,
        SMTP_PORT,
        timeout=60
    ) as server:

        server.ehlo()
        server.starttls()
        server.ehlo()

        if SMTP_USERNAME and SMTP_PASSWORD:
            server.login(
                SMTP_USERNAME,
                SMTP_PASSWORD
            )

        server.sendmail(
            FROM_EMAIL,
            recipients,
            msg.as_string()
        )


# ==========================================================
# MAIN
# ==========================================================

def main():
    print("Loading data...")

    df = build_master()

    # Hanya reminder >= 3 bulan
    reminder = df[
        (df["STATUS_KEMASKINI"] == "BELUM DIKEMASKINI")
        & (df["UMUR_BULAN"].notna())
        & (df["UMUR_BULAN"] >= 3)
    ].copy()

    print(
        f"Jumlah baucar reminder >=3 bulan: "
        f"{len(reminder):,}"
    )

    if reminder.empty:
        print("Tiada baucar untuk dihantar.")
        return

    # Group ikut ID
    grouped = reminder.groupby(
        "ID",
        dropna=False
    )

    sent_count = 0
    skipped_count = 0
    failed_count = 0

    for owner_id, rows in grouped:
        owner_id = str(owner_id).strip()

        owner_name = (
            rows["NAMA_EMEL"]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
        )

        if not owner_name.empty:
            owner_name = owner_name.iloc[0]
        else:
            owner_name = (
                rows["NAMA"]
                .fillna("")
                .astype(str)
                .str.strip()
                .replace("", pd.NA)
                .dropna()
            )

            owner_name = (
                owner_name.iloc[0]
                if not owner_name.empty
                else owner_id
            )

        owner_email = (
            rows["EMAIL_PEMILIK"]
            .fillna("")
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
        )

        if owner_email.empty:
            print(
                f"SKIP ID {owner_id} - "
                f"tiada email pemilik."
            )
            skipped_count += 1
            continue

        owner_email = owner_email.iloc[0]

        actual_to = owner_email
        actual_cc = GROUP_KEWANGAN_EMAIL

        # TEST MODE:
        # Semua email dialihkan kepada TEST_EMAIL
        if TEST_MODE:
            if not TEST_EMAIL:
                raise ValueError(
                    "TEST_MODE=true tetapi TEST_EMAIL kosong."
                )

            actual_to = TEST_EMAIL
            actual_cc = ""

        subject = (
            f"Peringatan Mingguan E-Filing BKA - "
            f"{len(rows):,} Baucar Belum Dikemaskini"
        )

        html_body = build_email_html(
            owner_name,
            owner_id,
            rows
        )

        if TEST_MODE:
            html_body = f"""
            <div style="padding:12px;background:#fff3cd;border:1px solid #ffe69c;">
                <b>TEST MODE</b><br>
                Pemilik sebenar: {owner_name}<br>
                ID sebenar: {owner_id}<br>
                Email sebenar: {owner_email}<br>
                CC sebenar: {GROUP_KEWANGAN_EMAIL}
            </div>
            <br>
            {html_body}
            """

        try:
            send_one_email(
                actual_to,
                actual_cc,
                subject,
                html_body
            )

            print(
                f"SENT ID {owner_id} -> "
                f"{actual_to} "
                f"({len(rows):,} baucar)"
            )

            sent_count += 1

        except Exception as exc:
            failed_count += 1

            print(
                f"FAILED ID {owner_id}: {exc}"
            )

    print("")
    print("========================================")
    print("RINGKASAN PENGHANTARAN")
    print("========================================")
    print(f"Berjaya dihantar : {sent_count}")
    print(f"Tiada email       : {skipped_count}")
    print(f"Gagal             : {failed_count}")
    print("========================================")


if __name__ == "__main__":
    main()

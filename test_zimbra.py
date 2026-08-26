import os
import smtplib
from email.message import EmailMessage

SMTP_SERVER = os.getenv("ZIMBRA_SMTP_SERVER", "mail.cidb.gov.my").strip()
SMTP_PORT = int(os.getenv("ZIMBRA_SMTP_PORT", "587"))
USERNAME = os.getenv("ZIMBRA_USERNAME", "").strip()
PASSWORD = os.getenv("ZIMBRA_PASSWORD", "").strip()
TEST_TO = os.getenv("ZIMBRA_TEST_TO", USERNAME).strip()

if not USERNAME:
    raise ValueError("ZIMBRA_USERNAME belum ditetapkan.")

if not PASSWORD:
    raise ValueError("ZIMBRA_PASSWORD belum ditetapkan.")

if not TEST_TO:
    raise ValueError("ZIMBRA_TEST_TO kosong.")

msg = EmailMessage()
msg["From"] = USERNAME
msg["To"] = TEST_TO
msg["Subject"] = "TEST SMTP ZIMBRA CIDB"
msg.set_content(
    "Ini adalah ujian penghantaran SMTP Zimbra CIDB.\n\n"
    "Jika emel ini diterima, sambungan SMTP dan authentication berjaya."
)

print("========== ZIMBRA SMTP TEST ==========")
print(f"SMTP_SERVER : {SMTP_SERVER}")
print(f"SMTP_PORT   : {SMTP_PORT}")
print(f"USERNAME    : {USERNAME}")
print(f"TEST_TO     : {TEST_TO}")
print("======================================")

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
        server.set_debuglevel(1)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(USERNAME, PASSWORD)
        server.send_message(
            msg,
            from_addr=USERNAME,
            to_addrs=[TEST_TO]
        )
    print("\nSUCCESS: EMAIL BERJAYA DIHANTAR")

except smtplib.SMTPAuthenticationError as exc:
    print("\nFAILED: SMTP AUTHENTICATION ERROR")
    print(exc)

except smtplib.SMTPNotSupportedError as exc:
    print("\nFAILED: SMTP FEATURE TIDAK DISOKONG")
    print(exc)

except (ConnectionRefusedError, TimeoutError, OSError) as exc:
    print("\nFAILED: CONNECTION ERROR")
    print(exc)

except Exception as exc:
    print("\nFAILED: ERROR LAIN")
    print(type(exc).__name__, exc)

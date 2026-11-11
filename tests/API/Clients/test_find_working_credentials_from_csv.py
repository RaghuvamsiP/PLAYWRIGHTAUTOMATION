"""
Validate report-provider credentials sourced from CSV files.

Each (username, password) row is posted to the report `process` endpoint and rows
that answer with HTTP 200 have their username and password printed. There are
three tests:

  * test_report_credentials_from_csv         -> CreditHeroScore
  * test_smartcredit_credentials_from_csv    -> SmartCredit (Base64 credentials)
  * test_myfreescorenow_credentials_from_csv -> MyFreeScoreNow (Base64 credentials)

Requests use the ``auth_api`` fixture from conftest.py (base URL + bearer token for
the configured account). The CLIENT_ID / CRO_ID values are tied to that account, so
adjust them if you switch the conftest credentials.
"""

import base64
import os


# --- Editable configuration -------------------------------------------------
# Requests go through the ``auth_api`` fixture (see conftest.py), which sets the
# base URL and bearer token; PROCESS_PATH is appended to that base URL.
PROCESS_PATH = "/api/report/process"

# CreditHeroScore
CSV_PATH = r"C:\Users\Admin\Downloads\chs.csv"
CLIENT_ID = 38

# SmartCredit
SMARTCREDIT_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "payloads", "smartcredit_credentials.csv"
)
SMARTCREDIT_CLIENT_ID = 47

# MyFreeScoreNow
MYFREESCORENOW_CSV_PATH = os.path.join(
    os.path.dirname(__file__), "..", "payloads", "myfreescorenow_credentials.csv"
)
MYFREESCORENOW_CLIENT_ID = 47

CRO_ID = 1003476
# ---------------------------------------------------------------------------


def _build_payload(user_name: str, password: str, client_id: int) -> dict:
    """Return the report/process payload with the CSV credentials filled in."""
    return {
        "clientId": client_id,
        "provider": "CreditHeroScore",
        "userName": user_name,
        "password": password,
        "ssn": "",
        "phone_number": "",
        "isSubmit": 1,
        "isContinueWithDuplicate": 0,
        "isReimport": 0,
        "isReportImportedPreviously": 0,
        "simpleAudit": 1,
        "lastImportDate": "",
        "teamId": 1,
        "auditTemplateId": "1",
        "generateSimpleAudit": 0,
        "croId": CRO_ID,
    }


def _b64(value: str) -> str:
    """Base64-encode a string the way the SmartCredit payload expects."""
    return base64.b64encode(value.encode("utf-8")).decode("ascii")


def _build_smartcredit_payload(user_name: str, password: str, client_id: int) -> dict:
    """Return the SmartCredit report/process payload (credentials Base64-encoded)."""
    return {
        "clientId": client_id,
        "provider": "SmartCredit",
        "userName": _b64(user_name),
        "password": _b64(password),
        "ssn": "",
        "phone_number": "",
        "isSubmit": 1,
        "isContinueWithDuplicate": 0,
        "isReimport": 0,
        "isReportImportedPreviously": 0,
        "simpleAudit": 0,
        "lastImportDate": 0,
        "teamId": 1,
        "auditTemplateId": "1",
        "generateSimpleAudit": 0,
        "croId": CRO_ID,
    }


def _build_myfreescorenow_payload(user_name: str, password: str, client_id: int) -> dict:
    """Return the MyFreeScoreNow report/process payload (credentials Base64-encoded)."""
    return {
        "clientId": client_id,
        "provider": "MyFreeScoreNow",
        "userName": _b64(user_name),
        "password": _b64(password),
        "ssn": "",
        "phone_number": "",
        "isSubmit": 1,
        "isContinueWithDuplicate": 0,
        "isReimport": 0,
        "isReportImportedPreviously": 0,
        "simpleAudit": 0,
        "lastImportDate": 0,
        "teamId": 1,
        "auditTemplateId": "1",
        "generateSimpleAudit": 0,
        "croId": CRO_ID,
    }


def _read_credentials(csv_path: str) -> list[tuple[str, str]]:
    """Read (email, password) pairs from the file.

    Accepts tab- or comma-separated rows, with or without an ``email,password``
    header, and skips blank lines.
    """
    credentials: list[tuple[str, str]] = []
    with open(csv_path, encoding="utf-8-sig") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in (line.split("\t") if "\t" in line else line.split(","))]
            # Drop a leading provider column if present (e.g. 3-column SmartCredit rows).
            if len(parts) >= 3 and parts[0].lower() in ("smartcredit", "creditheroscore"):
                parts = parts[1:]
            if len(parts) < 2:
                continue
            email, password = parts[0], parts[1]
            if not email or not password or email.lower() in ("email", "username"):
                continue
            credentials.append((email, password))
    return credentials


def test_chs_credentials_from_csv(auth_api):
    """Post the payload with each CSV credential and print the username/password
    of every row whose response code is 200.
    """
    credentials = _read_credentials(CSV_PATH)
    assert credentials, f"No credentials found in {CSV_PATH}"

    for user_name, password in credentials:
        payload = _build_payload(user_name, password, CLIENT_ID)
        response = auth_api.post(PROCESS_PATH, data=payload)
        if response.status == 200:
            print(f"username: {user_name} | password: {password}")


def test_smartcredit_credentials_from_csv(auth_api):
    """Post the payload with each SmartCredit CSV credential and print the
    username/password of every row whose response code is 200.
    """
    credentials = _read_credentials(SMARTCREDIT_CSV_PATH)
    assert credentials, f"No credentials found in {SMARTCREDIT_CSV_PATH}"

    for user_name, password in credentials:
        payload = _build_smartcredit_payload(user_name, password, SMARTCREDIT_CLIENT_ID)
        response = auth_api.post(PROCESS_PATH, data=payload)
        if response.status == 200:
            print(f"200 OK -> username: {user_name} | password: {password}")
        else:
            # Diagnostic: show why rows are not returning 200.
            print(f"{response.status} -> {user_name} | body: {response.text()[:200]}")


def test_myfreescorenow_credentials_from_csv(auth_api):
    """Post the payload with each MyFreeScoreNow CSV credential (Base64-encoded) and
    print the username/password of every row whose response code is 200.
    """
    credentials = _read_credentials(MYFREESCORENOW_CSV_PATH)
    assert credentials, f"No credentials found in {MYFREESCORENOW_CSV_PATH}"

    for user_name, password in credentials:
        payload = _build_myfreescorenow_payload(user_name, password, MYFREESCORENOW_CLIENT_ID)
        response = auth_api.post(PROCESS_PATH, data=payload)
        if response.status == 200:
            print(f"200 OK -> username: {user_name} | password: {password}")
        else:
            # Diagnostic: show why rows are not returning 200.
            print(f"{response.status} -> {user_name} | body: {response.text()[:200]}")

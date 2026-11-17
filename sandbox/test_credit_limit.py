"""Validate per-bureau credit utilization in the preview report response.

The rules follow the "Re-import Credit Utilization Logic" doc
(sandbox/utilization_rules.md). For each bureau, an account counts only when:

1. Account Status is "Open" (closed, paid, derogatory, transferred are out);
2. Credit Limit is greater than 0;
3. Account Type is revolving: it contains revolving / credit card / charge card /
   charge account / line of credit / HELOC, or is exactly CC, R or CH.
   Overdraft reserve accounts are excluded.

Negative balances count as 0. Per bureau:
    utilization      = balance / limit * 100, rounded to 2 decimals (0 if no limit)
    available_credit = limit - balance, floored at 0
Headline (current_credit_utilization) is pooled across the three bureaus:
    sum(balances) / sum(limits) * 100 -- not an average of bureau percentages.

The calculated figures are asserted against the app's own
data.first_import_summary block in the same response.

Providers name the balance field differently: Credit Hero Score, MyScoreIQ and
IdentityIQ use "Balance"; SmartCredit uses "Balance Owed".

The *_simple_audit tests cover the separate Simple Audit calculation
(sandbox/utilization_rules_2.md): per-bureau totals are asserted against the
stored data.simple_audit_data, and the audit's headline figures are printed.
"""

import json
from decimal import ROUND_HALF_UP, Decimal

import pytest

from crc_automation.config.settings import API_TEST_DATA_DIR

BUREAUS = ("Equifax", "TransUnion", "Experian")
CHS_RESPONSE = API_TEST_DATA_DIR / "chs_preview_report_response.json"
SC_RESPONSE = API_TEST_DATA_DIR / "sc_preview_report_response.json"
MSIQ_RESPONSE = API_TEST_DATA_DIR / "msiq_preview_report_response.json"
IDIQ_RESPONSE = API_TEST_DATA_DIR / "idiq_preview_report_response.json"

REVOLVING_KEYWORDS = (
    "revolving", "credit card", "charge card", "charge account",
    "line of credit", "heloc",
)
REVOLVING_CODES = {"CC", "R", "CH"}


def parse_money(value) -> float:
    """Convert '$16,052.00' to 16052.0; null, empty, '-' and 'N/A' count as 0.

    MyScoreIQ writes '-' for a value that is not reported.
    """
    if not value:
        return 0.0
    cleaned = str(value).replace("$", "").replace(",", "").replace("&nbsp;", "").strip()
    if cleaned in ("", "-", "N/A"):
        return 0.0
    return float(cleaned)


def percent(part: float, whole: float) -> float:
    """part / whole * 100 rounded half-up to 2 decimals, as the app does (5.675 -> 5.68).

    Python's round() would give 5.67 here, because 5.675 is not exact in binary.
    """
    if not whole:
        return 0.0
    value = Decimal(str(part)) * 100 / Decimal(str(whole))
    return float(value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def is_revolving(account_type) -> bool:
    if not account_type:
        return False
    text = str(account_type).strip()
    if text.upper() in REVOLVING_CODES:
        return True
    lowered = text.lower()
    if "overdraft" in lowered:
        return False
    return any(keyword in lowered for keyword in REVOLVING_KEYWORDS)


def counts_toward_utilization(details: dict) -> bool:
    """Apply the doc's three rules: open, limit > 0, revolving.

    The type check also reads "Account Type - Detail" (IdentityIQ, MyScoreIQ):
    Experian can report Account Type "Unknown" with detail "Credit Card", and
    the app counts that account as revolving.
    """
    status = str(details.get("Account Status") or "").strip().lower()
    return (
        status == "open"
        and parse_money(details.get("Credit Limit")) > 0
        and (
            is_revolving(details.get("Account Type"))
            or is_revolving(details.get("Account Type - Detail"))
        )
    )


def get_accounts(body: dict, balance_key: str) -> list[dict]:
    """Flatten account_summary into one row per account with each bureau's values.

    ``balance_key`` is the provider's field name for the balance.
    """
    accounts = []
    for entry in body["data"]["account_summary"]:
        for creditor, account in entry.items():
            row = {"creditor": creditor}
            for bureau in BUREAUS:
                details = account.get(bureau) or {}
                row[bureau] = {
                    "credit_limit": parse_money(details.get("Credit Limit")),
                    # Negative balances count as 0.
                    "balance": max(parse_money(details.get(balance_key)), 0.0),
                    "status": details.get("Account Status"),
                    "type": details.get("Account Type"),
                    "included": counts_toward_utilization(details),
                }
            accounts.append(row)
    return accounts


def summarize_by_bureau(accounts: list[dict]) -> dict:
    """Per-bureau totals from included accounts, plus the pooled headline %."""
    bureaus = {}
    for bureau in BUREAUS:
        included = [a[bureau] for a in accounts if a[bureau]["included"]]
        limit = sum(a["credit_limit"] for a in included)
        balance = sum(a["balance"] for a in included)
        bureaus[bureau] = {
            "total_credit_limit": limit,
            "total_balance": balance,
            "available_credit": max(limit - balance, 0.0),
            "utilization": percent(balance, limit),
            "account_count": len(included),
        }

    total_limit = sum(b["total_credit_limit"] for b in bureaus.values())
    total_balance = sum(b["total_balance"] for b in bureaus.values())
    pooled = percent(total_balance, total_limit)
    return {"bureaus": bureaus, "current_credit_utilization": pooled}


def print_included_accounts(accounts: list[dict]) -> None:
    """Print the accounts that count, sorted by creditor, then in bureau order."""
    rows = [
        (account["creditor"], BUREAUS.index(bureau), bureau, account[bureau])
        for account in accounts
        for bureau in BUREAUS
        if account[bureau]["included"]
    ]
    rows.sort(key=lambda row: (row[0].lower(), row[1]))

    print(f"\n{'Creditor':<26}{'Bureau':<12}{'Status':<10}{'Type':<20}{'Limit':>10}{'Balance':>10}")
    for creditor, _, bureau, b in rows:
        print(
            f"{creditor[:25]:<26}{bureau:<12}{b['status']:<10}"
            f"{str(b['type'])[:19]:<20}{b['credit_limit']:>10,.0f}{b['balance']:>10,.0f}"
        )


def print_comparison(summary: dict, expected: dict) -> None:
    print(f"\n{'Bureau':<12}{'Field':<20}{'Calculated':>14}{'App':>14}")
    for bureau in BUREAUS:
        for field, value in summary["bureaus"][bureau].items():
            print(f"{bureau:<12}{field:<20}{value:>14,.2f}{expected[bureau][field]:>14,.2f}")
    print(
        f"\nCurrent credit utilization: calculated "
        f"{summary['current_credit_utilization']:.2f}%"
    )


# --- Simple Audit -----------------------------------------------------------
# Rules from the "Simple Audit Calculations" doc (sandbox/utilization_rules_2.md).
# This is what the audit shows as "Total available revolving credit",
# "Current credit card balance" and "Credit Card Usage" -- a different
# calculation from first_import_summary above.

AUDIT_CODES = {"Equifax": "eq", "TransUnion": "tr", "Experian": "ex"}

# IdentityIQ, MyScoreIQ, PrivacyGuard, Sample, new MyFreeScoreNow: exact type
# match. "Credit Card" alone is NOT counted.
GENERIC_AUDIT_TYPES = {
    "revolving", "revolving or option", "revolving charge account",
    "revolving account", "credit card - revolving terms",
}

SMART_CREDIT = "smartcredit"
GENERIC = "generic"
# Not in the doc's provider table: CHS uses the generic type list but, judging
# by its stored simple_audit_data, skips accounts whose limit is $0.
CHS = "chs"


def audit_money(value) -> int:
    """Audit amounts drop cents: '$1,234.99' -> 1234."""
    return int(parse_money(value))


def round_half_up(value: float) -> int:
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def audit_counts_account(details: dict, bureau: str, rule: str) -> bool:
    if str(details.get("Account Status") or "").strip().lower() != "open":
        return False
    account_type = str(details.get("Account Type") or "").strip().lower()
    if rule == SMART_CREDIT:
        # Equifax/Experian: credit card only. TransUnion also takes revolving.
        is_card = "credit card" in account_type
        if bureau == "TransUnion":
            is_card = is_card or "revolving" in account_type
        return is_card and audit_money(details.get("Credit Limit")) > 0
    if account_type not in GENERIC_AUDIT_TYPES:
        return False
    if rule == CHS:
        return audit_money(details.get("Limit") or details.get("Credit Limit")) > 0
    return True  # generic: a $0 limit still counts the bureau


def simple_audit_totals(body: dict, rule: str) -> dict:
    """Per-bureau limit, balance and card count, as the audit transformer stores them."""
    totals = {b: {"limit": 0, "balance": 0, "count": 0} for b in BUREAUS}
    for entry in body["data"]["account_summary"]:
        for account in entry.values():
            for bureau in BUREAUS:
                details = account.get(bureau) or {}
                if not audit_counts_account(details, bureau, rule):
                    continue
                if rule == SMART_CREDIT:
                    limit = audit_money(details.get("Credit Limit"))
                    balance = max(audit_money(details.get("Balance Owed")), 0)
                else:
                    limit = audit_money(details.get("Limit") or details.get("Credit Limit"))
                    balance = audit_money(details.get("Balance") or details.get("Balance Owed"))
                totals[bureau]["limit"] += limit
                totals[bureau]["balance"] += balance
                totals[bureau]["count"] += 1
    return totals


def usage_rating(usage: int) -> str:
    if usage < 10:
        return "Excellent"
    if usage < 30:
        return "Good"
    if usage < 50:
        return "Fair"
    if usage < 75:
        return "Poor"
    return "Very Poor"


def simple_audit_figures(totals: dict) -> dict:
    """The three headline figures the audit shows.

    available = round(sum of limits / 3)       -- always 3, even for empty bureaus
    balance   = round(sum of balances / n)     -- n = bureaus with a counted card
    usage     = round(average over n of round(balance * 100 / limit))
    """
    with_cards = [b for b in BUREAUS if totals[b]["count"]]
    n = len(with_cards)
    per_bureau_pct = {
        b: round_half_up(totals[b]["balance"] * 100 / totals[b]["limit"])
        for b in with_cards
        if totals[b]["limit"]
    }
    usage = round_half_up(sum(per_bureau_pct.values()) / n) if n else 0
    return {
        "available": round_half_up(sum(totals[b]["limit"] for b in BUREAUS) / 3),
        "balance": round_half_up(sum(totals[b]["balance"] for b in BUREAUS) / n) if n else 0,
        "usage": usage,
        "rating": usage_rating(usage),
        "per_bureau_pct": per_bureau_pct,
    }


def check_simple_audit(response_file, rule: str) -> None:
    body = json.loads(response_file.read_text(encoding="utf-8"))
    audit = body["data"]["simple_audit_data"]
    stored = audit["simple_audit_account_summary"]
    totals = simple_audit_totals(body, rule)
    figures = simple_audit_figures(totals)

    print(f"\n{'Bureau':<12}{'Field':<10}{'Calculated':>12}{'Stored':>12}")
    for bureau in BUREAUS:
        code = AUDIT_CODES[bureau]
        for field, key in (
            ("limit", f"simple_audit_credit_limit_{code}"),
            ("balance", f"simple_audit_balance_{code}"),
            ("count", f"simple_audit_credit_limit_{code}_cnt"),
        ):
            print(f"{bureau:<12}{field:<10}{totals[bureau][field]:>12,}{int(stored.get(key) or 0):>12,}")

    print(f"\nPer-bureau usage: {figures['per_bureau_pct']}")
    print(f"Total available revolving credit: ${figures['available']:,}")
    print(f"Current credit card balance:      ${figures['balance']:,}")
    print(f"Credit Card Usage:                {figures['usage']}% ({figures['rating']})")

    for bureau in BUREAUS:
        code = AUDIT_CODES[bureau]
        for field, key in (
            ("limit", f"simple_audit_credit_limit_{code}"),
            ("balance", f"simple_audit_balance_{code}"),
            ("count", f"simple_audit_credit_limit_{code}_cnt"),
        ):
            assert totals[bureau][field] == int(stored.get(key) or 0), (
                f"{bureau} {field}: calculated {totals[bureau][field]}, stored {stored.get(key)}"
            )

    # CHS supplies its own audit figures, which replace the calculation.
    if "totalAvailableRevolvingCredit" in audit:
        print(
            f"\nCHS payload overrides the audit: available "
            f"${audit['totalAvailableRevolvingCredit']:,}, balance "
            f"${audit['currentCreditCardBalance']:,}, usage {audit['credit_utilization']}%"
        )


def check_credit_utilization(response_file, balance_key: str) -> None:
    body = json.loads(response_file.read_text(encoding="utf-8"))
    accounts = get_accounts(body, balance_key)
    summary = summarize_by_bureau(accounts)
    app = body["data"]["first_import_summary"]
    expected = app["credit_utilization_by_bureau"]

    print(f"\nAccounts found: {len(accounts)}")
    print_included_accounts(accounts)
    print_comparison(summary, expected)
    print(f"App current credit utilization:        {app['current_credit_utilization']:.2f}%")

    assert accounts, "No accounts found in account_summary"

    for bureau in BUREAUS:
        calculated = summary["bureaus"][bureau]
        for field, value in calculated.items():
            assert value == pytest.approx(expected[bureau][field], abs=0.01), (
                f"{bureau} {field}: calculated {value}, app shows {expected[bureau][field]}"
            )

    assert summary["current_credit_utilization"] == pytest.approx(
        app["current_credit_utilization"], abs=0.01
    ), "Pooled current utilization does not match the app"

    # First import: Starting equals Current, and there is no Prior yet (null, not 0).
    assert app["starting_credit_utilization"] == app["current_credit_utilization"]
    assert app["prior_credit_utilization"] is None


def test_chs_credit_utilization_per_bureau():
    check_credit_utilization(CHS_RESPONSE, "Balance")


def test_msiq_credit_utilization_per_bureau():
    check_credit_utilization(MSIQ_RESPONSE, "Balance")


def test_idiq_credit_utilization_per_bureau():
    check_credit_utilization(IDIQ_RESPONSE, "Balance")


def test_smart_credit_utilization_per_bureau():
    body = json.loads(SC_RESPONSE.read_text(encoding="utf-8"))
    # Guard against a silent all-zero pass if the key name is wrong.
    has_balance_owed = any(
        "Balance Owed" in (account.get(bureau) or {})
        for entry in body["data"]["account_summary"]
        for account in entry.values()
        for bureau in BUREAUS
    )
    assert has_balance_owed, "SmartCredit response has no 'Balance Owed' field"
    check_credit_utilization(SC_RESPONSE, "Balance Owed")


def test_chs_simple_audit():
    check_simple_audit(CHS_RESPONSE, CHS)


def test_msiq_simple_audit():
    check_simple_audit(MSIQ_RESPONSE, GENERIC)


def test_idiq_simple_audit():
    check_simple_audit(IDIQ_RESPONSE, GENERIC)


def test_smart_credit_simple_audit():
    check_simple_audit(SC_RESPONSE, SMART_CREDIT)

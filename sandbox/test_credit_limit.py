"""Sum credit limit and balance per bureau from the preview report response.

Every account is checked; null/empty values count as $0. For each bureau, an
account whose Credit Limit is $0 or null is left out, so its balance is not summed.
Prints each account's values, then the per-bureau summary
(Credit Limit / Balance / Utilization) and the overall totals
(Total Credit Limit, Total Balance, Available Credit).
"""

import json

from crc_automation.config.settings import API_TEST_DATA_DIR

BUREAUS = ("Equifax", "TransUnion", "Experian")
SAMPLE_RESPONSE = API_TEST_DATA_DIR / "preview_report_response.json"


def parse_money(value) -> float:
    """Convert '$16,052.00' to 16052.0; null/empty values count as 0."""
    if not value:
        return 0.0
    return float(str(value).replace("$", "").replace(",", ""))


def get_accounts(body: dict) -> list[dict]:
    """Flatten account_summary into one row per account with each bureau's values."""
    accounts = []
    for entry in body["data"]["account_summary"]:
        for creditor, account in entry.items():
            row = {"creditor": creditor}
            for bureau in BUREAUS:
                details = account.get(bureau) or {}
                row[bureau] = {
                    "credit_limit": parse_money(details.get("Credit Limit")),
                    "balance": parse_money(details.get("Balance")),
                }
            accounts.append(row)
    return accounts


def summarize_by_bureau(accounts: list[dict]) -> dict:
    """Sum credit limit and balance per bureau and compute utilization and totals."""
    bureaus = {b: {"credit_limit": 0.0, "balance": 0.0} for b in BUREAUS}

    for account in accounts:
        for bureau in BUREAUS:
            limit = account[bureau]["credit_limit"]
            # Skip the balance when the bureau reports no credit limit ($0 or null).
            if not limit:
                continue
            bureaus[bureau]["credit_limit"] += limit
            bureaus[bureau]["balance"] += account[bureau]["balance"]

    for totals in bureaus.values():
        limit = totals["credit_limit"]
        totals["utilization"] = round(totals["balance"] / limit * 100) if limit else 0

    total_limit = sum(t["credit_limit"] for t in bureaus.values())
    total_balance = sum(t["balance"] for t in bureaus.values())
    return {
        "bureaus": bureaus,
        "total_credit_limit": total_limit,
        "total_balance": total_balance,
        "available_credit": total_limit - total_balance,
    }


def print_accounts(accounts: list[dict]) -> None:
    """Print each account's credit limit and balance for every bureau."""
    header = f"{'#':<4}{'Creditor':<28}" + "".join(
        f"{b + ' Limit':>18}{b + ' Bal':>18}" for b in BUREAUS
    )
    print("\n" + header)
    print("-" * len(header))
    for i, account in enumerate(accounts, start=1):
        line = f"{i:<4}{account['creditor'][:27]:<28}"
        for bureau in BUREAUS:
            line += (
                f"{account[bureau]['credit_limit']:>18,.0f}"
                f"{account[bureau]['balance']:>18,.0f}"
            )
        print(line)


def print_summary(summary: dict) -> None:
    """Print the per-bureau table and overall totals."""
    print(f"\n{'Bureau':<12}{'Credit Limit':>15}{'Balance':>15}{'Utilization':>13}")
    for bureau, t in summary["bureaus"].items():
        print(
            f"{bureau:<12}{t['credit_limit']:>15,.0f}{t['balance']:>15,.0f}"
            f"{t['utilization']:>12}%"
        )
    print(f"\nTotal Credit Limit: ${summary['total_credit_limit']:,.0f}")
    print(f"Total Balance:      ${summary['total_balance']:,.0f}")
    print(f"Available Credit:   ${summary['available_credit']:,.0f}")


def test_credit_limit_and_balance_per_bureau():
    body = json.loads(SAMPLE_RESPONSE.read_text(encoding="utf-8"))
    accounts = get_accounts(body)
    summary = summarize_by_bureau(accounts)

    print(f"\nAccounts found: {len(accounts)}")
    print_accounts(accounts)
    print_summary(summary)

    assert accounts, "No accounts found in account_summary"
    bureaus = summary["bureaus"]
    assert summary["total_credit_limit"] == sum(b["credit_limit"] for b in bureaus.values())
    assert summary["total_balance"] == sum(b["balance"] for b in bureaus.values())
    assert summary["available_credit"] == (
        summary["total_credit_limit"] - summary["total_balance"]
    )

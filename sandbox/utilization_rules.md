# Credit Utilization Rules

<!-- Paste the doc content below this line, then save the file. -->


Re-import Credit Utilization Logic
11 Nov 2026 · @Tulasi
On re-import, the Progress Report shows Credit Utilization per bureau (Total Credit Limit, Total Balance, Available Credit, Utilization) plus a Starting / Prior / Current history. The current figures are the bureaus' own revolving-trade numbers; only the historic rows are recalculated from stored accounts.
What the feature shows
The re-import summary returns a credit_utilization_by_bureau block with one row per bureau (TransUnion, Experian, Equifax), each carrying five fields:
Field
Meaning
How it is produced
total_credit_limit
Total credit line of open revolving trades
Bureau code RE28S, read as-is
total_balance
Total balance of open revolving trades
Bureau code RE33S, read as-is
available_credit
Credit still unused
Derived: RE28S − RE33S, floored at 0
utilization
Revolving utilization %
Bureau code RE34S, read as-is
account_count
Open revolving trades the figures cover
Bureau code RE02S
Beside the table, the summary carries three headline rows: starting_credit_utilization (first import ever), prior_credit_utilization (import just before this one), and current_credit_utilization (this import). All figures are rounded to 2 decimals; the frontend rounds further for display.
Current import: the bureau's own numbers
For the import being processed, we do not add up accounts. We read each bureau's own revolving summary attributes out of the raw report's CREDIT_SUMMARY_TUI / CREDIT_SUMMARY_XPN / CREDIT_SUMMARY_EFX blocks, while the report is being processed (ProcessReportService, via CreditUtilizationByBureau):
• RE28S — Total credit line of open revolving trades verified in the past 12 months
• RE33S — Total balance of open revolving trades verified in the past 12 months
• RE34S — Utilization for those trades (the bureau's own percentage)
• RE02S — Number of open revolving trades (shown as account_count)
Attributes are matched by the code before the colon in the attribute name (e.g. RE28S: Total credit line...). Values are cleaned of $, commas and % before parsing.
Why the bureau's numbers and not our own sum: the percentage shown always matches the limit and balance shown beside it, and it agrees with how the existing aggregate Credit Utilization (Simple Audit) already reads RE34S. A value of N/A or the bureau sentinels -4 / -5 means "not reported" and is treated as missing, never as a number.
Derived values and edge cases
Available Credit is the only derived figure: RE28S minus RE33S, floored at 0.00 — it never shows negative even when the balance exceeds the limit.
Case
Behavior
Bureau block missing from the report
All five fields return 0 for that bureau; the other bureaus still fill in
Both RE28S and RE33S missing / N/A
Bureau treated as empty: all zeros
Only one of limit / balance present
The missing one defaults to 0
RE34S is N/A but limit and balance exist
Utilization computed as balance / limit × 100 (0 when limit is 0). Verified across 904 QA reports that N/A only occurs when both are 0
Balance higher than limit
Utilization shows over 100% (the bureau's own figure, uncapped); Available Credit shows 0.00
No revolving accounts vs. revolving accounts with nothing owed
Told apart by account_count: 0 accounts vs. a positive count with 0%
Value is N/A or bureau sentinel -4 / -5
Treated as not reported, never as a number
Starting / Prior / Current headline
No past utilization figure is stored anywhere, so the history is derived by re-running the calculation over the reports already kept in crd_cr_source (UtilizationHistory):
Row
Which import
How it is calculated
Starting
The client's first import ever (lowest iid). Never changes
Recalculated from that report's stored accounts
Prior
The import immediately before the current one (highest iid). Moves forward on every re-import
Recalculated from that report's stored accounts
Current
The import being processed
Pooled from the bureaus' own per-bureau figures above
Each headline is one percentage pooled across bureaus: total balance across all three bureaus ÷ total credit limit across all three bureaus × 100 — not an average of the three bureau percentages. Both the bureau-sourced Current and the account-derived history share the same pooling code, so they cannot combine bureaus differently.
Starting and Prior return null (not 0) when there is no earlier import to read — 0 would read as "they were at 0%", which is a different claim. Stored reports whose payload moved to S3 are read back from S3, at most two single-row reads per re-import.
How historic values are recalculated
Stored reports keep only the account list, never the bureau summary codes, so Starting and Prior are rebuilt from accounts (AccountUtilizationCalculator). Per bureau, an account counts toward the totals only when all three hold:
1.  Account Status is "open" — closed, paid, derogatory and transferred accounts are excluded, so a charged-off card does not inflate utilization.
2.  It has a credit limit greater than 0 — a zero or missing limit makes utilization meaningless for that account, so it is left out of both numerator and denominator.
3.  Its account type is revolving — the type contains revolving / credit card / charge card / charge account / line of credit / HELOC, or is one of the IdentityIQ abbreviations CC, R, CH. Overdraft reserve checking accounts are excluded. This matches the existing Simple Audit transformers.
Money values are cleaned of $, commas and the   entity that scraped reports carry. Negative balances count as 0.
Because of this, a historic percentage can differ slightly from what the bureau said at the time: the bureau measures "open revolving trades verified in the past 12 months", while this counts open revolving accounts carrying a limit. Expected, not a defect, when Starting and Current look slightly inconsistent for the same client.
Why Credit Audit and Import Summary differ (CHS-447, CHS-448)
The two screens are built from different parts of the same report, by design of the pre-existing Credit Audit code — so a mismatch between them is expected with the current logic, not a calculation error in either screen.

Credit Audit (Simple Audit)
Import Summary
Utilization %
Average of the bureaus' RE34S percentages. A bureau is skipped when its RE34S is 0, N/A or it has no open revolving trades. Values truncated to whole numbers before averaging
Total balance ÷ total limit × 100, pooled across all three bureaus' dollars
Limit / balance
One combined set of PT-code figures from the report's top-level CREDIT_SUMMARY block (PT111 total credit limit, PT017 revolving balance, PT179 card balance) — each account counted once
Sum of each bureau's own RE28S / RE33S — an account reported to two bureaus is counted at both
CHS-447 (limit $2,000 vs $4,000, balance $3,808 vs $3,773): summing RE28S across bureaus counts the same card once per bureau that reports it — a $2,000 card on two bureaus shows $4,000. The small balance gap is each bureau reporting its own balance as of its own verification date, versus the combined PT figure.
CHS-448 (65% vs 6%): an average of percentages and a dollar-pooled percentage are different measures. The gap gets extreme when only one bureau passes the audit's RE34S > 0 filter (its 65% becomes the whole average) while another bureau contributes a large credit line with a low balance to the pooled dollars, dragging the pooled figure down to 6%.
To make the screens match, one side has to adopt the other's method — a product decision: either the Import Summary averages RE34S the way the audit does (keeps the audit as-is, but the % then won't match the limit and balance shown beside it), or the audit switches to the pooled figure (internally consistent, but changes a long-standing audit number). Worth confirming against the actual report data on the QA client before picking.
QA notes
• All figures are rounded to 2 decimals in the payload; the frontend rounds further for display.
• Per-bureau rows always come back for all three bureaus, zeros when a bureau wasn't pulled.
• On the very first import there is no Starting/Prior — both are null.
• A bureau whose data can't be read logs a warning and returns zeros; it never blocks the summary.
"""
CloudMail Wallet Transaction Tests
1) Capture debitedAmount from debit endpoint
2) Calculate sum of debit transactions and validate against debitedAmount
"""

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"
crc_user_id = 1002881

debited_amount = 0


# -------------------------------------------------------------------
# 1) Capture debitedAmount from debit endpoint
# -------------------------------------------------------------------
def test_get_debited_amount(request_context):
    """Capture debitedAmount from the debit endpoint"""
    global debited_amount
    response = request_context.get(
        f"{base_url}/transactions/debit/{crc_user_id}/cloudmail"
    )
    assert response.status == 200, f"Request failed with status {response.status}"

    data = response.json()
    assert data['status'] == 'success'
    assert data['message'] == 'Debit transactions retrieved successfully'

    debited_amount = data['data']['debitedAmount']
    print(f"\ndebitedAmount: {debited_amount}")


# -------------------------------------------------------------------
# 2) Calculate sum of debit transactions and validate against debitedAmount
# -------------------------------------------------------------------
def test_debit_sum_matches_debited_amount(request_context):
    """Sum all debit type transactions and validate against debitedAmount"""
    total = 0

    # Fetch first page to get last_page count
    response = request_context.get(
        f"{base_url}/transactions/{crc_user_id}/cloudmail"
    )
    assert response.status == 200, f"Page 1 request failed with status {response.status}"

    data = response.json()
    assert data['status'] == 'success'
    assert data['message'] == 'Wallet transactions retrieved successfully'
    last_page = data['data']['transactions']['last_page']
    print(f"\nTotal pages: {last_page}")

    # Process first page
    for transaction in data['data']['transactions']['data']:
        if transaction['type'] == 'debit':
            total += transaction['amount']

    # Process remaining pages
    for page in range(2, last_page + 1):
        response = request_context.get(
            f"{base_url}/transactions/{crc_user_id}/cloudmail",
            params={"page": page}
        )
        assert response.status == 200, f"Page {page} request failed with status {response.status}"

        data = response.json()
        for transaction in data['data']['transactions']['data']:
            if transaction['type'] == 'debit':
                total += transaction['amount']

    debit_total = round(total, 2)
    print(f"\nComputed Debit Sum: {debit_total}")
    print(f"debitedAmount: {debited_amount}")

    assert debit_total == round(debited_amount, 2), (
        f"Mismatch: {debit_total} != {debited_amount}"
    )

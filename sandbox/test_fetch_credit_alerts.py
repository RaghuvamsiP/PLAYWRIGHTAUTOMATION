import requests

BASE_URL = "https://array.io/api/alerts/v2"
HEADERS = {
    "Accept": "application/json",
    "x-array-server-token": "D34328E2-4150-4AD3-9749-EFC14BCD8BFE",
}

USER_IDS = [
    "68670956-679893",
    "68671105-349235",
    "27960074-059609",
    "68671308-356148",
    "68671333-043938",
    "68417846-766517",
    "68671371-919501",
    "68671391-339119",
    "68671469-000176",
    "23768286-627388",
    "21963908-141289",
    "68671500-159660",
    "68671532-840385",
    "61860168-787956",
    "51995692-725425",
    "68671702-892890",
    "43501873-505165",
    "68671924-020821",
    "68671994-016167",
    "13685711-081154",
    "68672098-662696",
    "55980877-777488",
    "68672159-773673",
    "68672302-879539",
    "68672374-971717",
    "68672519-858894",
    "68672539-550758",
    "22069838-498542",
    "68672695-262169",
    "68672767-958884",
    "68518343-187904",
    "4005368-675132",
    "3999333-230339",
    "b2a61b31-ff8d-492f-aa7d-c18715833f1c",
    "68673177-043694",
    "49296235-951179",
    "68673196-328651",
    "68673205-820991",
    "68673207-688285",
    "53085784-307899",
    "68673570-489952",
    "35034649-670692",
    "68673834-749259",
    "68674009-194130",
    "68674102-270409",
    "68674196-782585",
    "68674222-234535",
    "68674226-786125",
    "68674272-756706",
    "58967802-071739",
]


def test_fetch_alerts_for_users():
    """For each user id, fetch alerts and print alertId + alertType for each alert."""
    failures = []

    for userid in USER_IDS:
        params = {"userId": userid, "offset": 0, "count": 100, "bureau": "tui"}
        response = requests.get(BASE_URL, params=params, headers=HEADERS)

        if response.status_code != 200:
            failures.append((userid, response.status_code))
            print(f"\nUserId: {userid}  FAILED status={response.status_code}  {response.text[:200]}")
            continue

        alerts = response.json().get("userAlerts", [])
        print(f"\nUserId: {userid}  ({len(alerts)} alerts)")
        for alert in alerts:
            print(f"  alertId={alert.get('alertId')}  alertType={alert.get('alertType')}")

    assert not failures, f"{len(failures)} user(s) failed: {failures}"

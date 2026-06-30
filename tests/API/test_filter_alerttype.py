import pytest
import requests

BASE_URL = "https://array.io/api/alerts/v2"
TOKEN = "D34328E2-4150-4AD3-9749-EFC14BCD8BFE"
LIST_HEADERS = {"x-array-server-token": TOKEN}
DETAIL_HEADERS = {
    "Accept": "application/json",
    "x-array-server-token": TOKEN
}
TARGET_ALERT_TYPES = {
    "NewBankruptcy",
    "DelinquentAccount",
    "FraudAlert",
    "ImprovedAccount",
    "NewAccount",
    "NewAddress"
}

USER_IDS = [
    "68690115-466133",
    "68690119-725852",
    "57220699-543098",
    "68690169-790763",
    "68690177-146614",
    "9429641-657234",
    "68690237-225304",
    "26481213-486259",
    "68690283-316582",
    "68690301-361366",
    "68690331-016380",
    "68690332-215370",
    "33192060-165642",
    "68690370-454078",
    "68690371-820457",
    "68690419-260139",
    "14227255-426109",
    "3453868-829124",
    "68690519-862998",
    "68690712-229057",
    "68690746-335884",
    "68690831-619621",
    "68690898-647315",
    "68690921-331627",
    "40718201-532646",
    "68691019-495338",
    "68626240-601722",
    "68691067-376304",
    "30849539-301033",
    "68691194-490654",
    "68691217-066719",
    "30972220-613273",
    "4221625-726554",
    "68691546-863075",
    "55897203-290489",
    "68691643-028374",
    "68691745-311485",
    "68691816-148827",
    "68691870-408210",
    "68691946-912513",
    "68692032-346397",
    "66160981-711875",
    "68692099-102776",
    "63211616-820792",
    "68692186-671302",
    "68692193-304970",
    "68692254-298698",
    "68692278-157448",
    "13846165-114021",
    "68692327-865363",
    "68692335-331993",
    "68692420-185814",
    "60521320-994559",
    "68692518-423240",
    "32295373-940589",
    "68692563-722053",
    "68692580-142357",
    "3621019-910514",
    "68692608-557411",
    "68692620-996009",
    "68692623-206718",
    "68692633-783531",
    "68692723-840537",
    "68692731-203194",
    "68692736-255577",
    "68692742-042656",
    "68692766-801475",
    "68692771-259788",
    "25614054-279869",
    "68692804-648704",
    "68692827-607460",
    "33789621-060677",
    "62659635-936729",
    "68692985-733741",
    "68693005-710868",
    "63200990-050087",
    "68693062-744392",
    "68693139-383461",
    "58344223-002785",
    "17883563-255058",
    "68693346-706367",
    "38702828-182106",
    "68693379-313240",
    "68693407-544502",
    "68693413-444572",
    "68693512-958503",
    "50265498-752082",
    "68693715-560310",
    "68693780-538795",
    "68693835-331322",
    "68693878-772987",
    "14429064-242546",
    "68693898-679954",
    "68693995-767616",
    "68694154-420265",
    "65334042-474266"
]


def _fetch_alert_ids(userid):
    """Return the list of alert ids for a given user."""
    url = f"{BASE_URL}?userId={userid}&offset=0&count=100&bureau=tui"
    response = requests.get(url, headers=LIST_HEADERS)
    assert response.status_code == 200, f"Failed for userId {userid}: {response.status_code}"
    data = response.json()
    return [alert.get('id') for alert in data.get('userAlerts', []) if alert.get('id') is not None]


def test_fetch_alert_details(userid=None, alertid=None):
    """Fetch alert details for a specific alert id + userid and return the alertType.

    When pytest collects this without arguments it is skipped — it is intended to
    be called from test_filter_alerts_by_type as a helper.
    """
    if userid is None or alertid is None:
        pytest.skip("Helper — call with userid and alertid from another test.")

    url = f"{BASE_URL}/{alertid}"
    params = {"bureau": "tui", "userId": userid}
    response = requests.get(url, params=params, headers=DETAIL_HEADERS)
    if response.status_code != 200:
        return None
    data = response.json()
    return data.get('details', {}).get('alertType')


def test_filter_alerts_by_type():
    """For each userid, fetch alert ids, look up the alertType for each, and
    list the alert ids whose alertType is one of the target types."""
    matches_by_user = {}

    for userid in USER_IDS:
        alert_ids = _fetch_alert_ids(userid)
        matched = []
        for alertid in alert_ids:
            alert_type = test_fetch_alert_details(userid, alertid)
            if alert_type in TARGET_ALERT_TYPES:
                matched.append((alertid, alert_type))

        if matched:
            matches_by_user[userid] = matched
            print(f"\nUserId: {userid}")
            for aid, atype in matched:
                print(f"  AlertId: {aid}  ->  {atype}")

    print("\n=== Summary (userid -> matching alert ids) ===")
    for userid, items in matches_by_user.items():
        ids_only = [aid for aid, _ in items]
        print(f"{userid}: {ids_only}")

    if not matches_by_user:
        print("No alerts matched the target alert types.")

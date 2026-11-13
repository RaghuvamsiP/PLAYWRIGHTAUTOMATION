import requests

# GET cloudmail "active" errors and count how many letter_id values come back.
BASE_URL = "https://d2287otoiq6o1c.cloudfront.net/api/cloudmail/errors"

# NOTE: bearer tokens are short-lived — replace this when it expires.
TOKEN = (
    "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjkxZTkwMTQ1MzExNjMwMGRmZjRh"
    "OTJkM2ZhNTczZTgxMTczNmYyZmY2NzhjM2Q1M2IzZTY2ZWVjMzRiODc0MzU1YTUwODJlYzgz"
    "ZGJlYmQzIiwiY29tcGFueV9uYW1lIjoiU0NTIFNPTFVUSU9OUyIsImZpcnN0X25hbWUiOiJS"
    "YWtoZW0iLCJsYXN0X25hbWUiOiJIYXd0aG9ybmUiLCJhZG1pbl9lbWFpbCI6ImluZm9Ac2Ns"
    "ZWVuc29sdXRpb25zLmNvbSIsInVzZXJfaWQiOjI4NjkzMzcsInJlZ19pZCI6Nzk2NjEsImJp"
    "bGxpbmdfcmVmX2lkIjpudWxsLCJ1c2VyX3R5cGUiOiJhZG1pbiIsImFjY291bnRfc3RhdHVz"
    "IjoiYWN0aXZlIiwicmVjdXJseV9wYXltZW50X3N0YXR1cyI6InBhaWQiLCJjb3VudHJ5X2Nv"
    "ZGUiOjIyNCwiY291bnRyeV9uYW1lIjoiVW5pdGVkIFN0YXRlcyIsInR3b19kaWdpdF9jb3Vu"
    "dHJ5X2NvZGUiOiJVUyIsImN1cnJlbmN5X2NvZGUiOiJVU0QiLCJjdXJyZW5jeV9zeW1ib2wi"
    "OiIkIiwidGltZXpvbmUiOiJBbWVyaWNhL0NoaWNhZ28iLCJwbGFuX25hbWUiOiJTY2FsZSIs"
    "ImlzX2Vhcmx5X2FjY2VzcyI6MSwiaXNfcHJlX2xhdW5jaCI6ZmFsc2UsImNoYXJnZWJlZV9l"
    "bnJvbGxlZCI6ZmFsc2UsImNoYXJnZWJlZV9lbmFibGVkIjpmYWxzZSwiY3JjX2JpbGxpbmdf"
    "ZW5hYmxlZCI6ZmFsc2UsInB1cmNoYXNlZF9tYXN0ZXJjbGFzcyI6Im5vIiwiaXNfc2lnbmVk"
    "Ijp0cnVlLCJpYXQiOjE3ODA2NDQ3NzMsIm5iZiI6MTc4MDY0NDc3MywiZXhwIjoxNzgwNzMx"
    "MTczLCJzaWdudXBfc3RhdHVzIjoiY29tcGxldGUifQ.Qcl-AgbIXIVbAwohz-R9a9sO05hTD"
    "f3bVRyhtRUtNsmMliGPLDEQHctxXaRMnsWUKz2-PpxMoYo-r5Lio6XlgirQmIIozOCb7hK3X"
    "VVnJBCxh5MeMy5HmGiHFze6INo-lln8ElXoTwX_TeNG0evfrZYH4EU0zONeEzpy-pwHkrZtQ"
    "rHCVZmsoQwX06GUM0JhwCw1-6g1dBdTaGIT-KIpmb33_88XQwET9-Ayb62gBGjtrXmAjhquZ"
    "WRc1_yrO7KplarIAPYbhCB81K7qUbVyxve5tL0KcJ2ae4nlHTFkCzImuYV7v-YaHQpYbmJO_"
    "4lv2vKstwCHHKJU4byiq2KpA_4JdKNmu8XBov86R7p7UCr_h7M58nJ_0SXbMNN1cofZUh8qy"
    "Y3HOgBMs2XPNnVCtV8WtJ2cwM1Mq3NUtKeTk-UAFHNcrTlU35vEnuUcihjQaptQFlLqetn2J"
    "480xjdYNHaYOGt4jzrN_VbSenReeGZCsszracIY24X55B09cLUTp56j8Ld0Irl3BE4xSmEy3"
    "52bDCQWUmTy_btYVnPkLnif-M7vgJYY6w33-NBY_3QCgul0q7ZbCSyzq0H3yziUmkKDLxH9Z"
    "8OkUd5p9UK39k36_u3epXY2upiuG2P1UXHO-99m6S08ApK0wI4ZfCkp47CWJ8nrhn_VcO_sB"
    "wCHHoU"
)

HEADERS = {
    "Accept": "application/json",
    "Authorization": f"Bearer {TOKEN}",
}


def test_count_letter_id_in_active_errors():
    """GET active cloudmail errors and count the letter_id values in the response."""
    response = requests.get(BASE_URL, params={"type": "active"}, headers=HEADERS)
    assert response.status_code == 200, (
        f"Expected 200 but got {response.status_code}: {response.text[:200]}"
    )

    data = response.json()
    errors = data.get("errors", [])

    letter_ids = [e["letter_id"] for e in errors if "letter_id" in e]
    unique_letter_ids = set(letter_ids)

    print(f"\nqueue_failed_count : {data.get('queue_failed_count')}")
    print(f"errors in response : {len(errors)}")
    print(f"letter_id count    : {len(letter_ids)}")
    print(f"unique letter_id   : {len(unique_letter_ids)}")

    # Every error row should carry a letter_id.
    assert len(letter_ids) == len(errors), "Some error rows are missing 'letter_id'"
    assert len(letter_ids) > 0, "Expected at least one letter_id in the response"

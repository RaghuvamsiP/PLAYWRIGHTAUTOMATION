"""
AI Letter Templates List API Test

GET: https://d2z6bx74pusiw2.cloudfront.net/api/library?page={n}&limit=20

Walks pages 1..7 and collects the `id` of every item whose
`isAILetter` flag is true into a single list.
"""

LIBRARY_URL = "https://d2z6bx74pusiw2.cloudfront.net/api/library"
START_PAGE = 1
END_PAGE = 7
PAGE_LIMIT = 20

AUTH_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJpZCI6IjBhOTNkZGEyM2UyYjEwZDhhNDYzNjA5OGQ2NGY5ZTU5NWY5YmY0MmI2MzMwZmI3YjExMmRjMjhhMmQyNTY2ZjRiYjU1NThiYjViMGY3MjkwIiwiY29tcGFueV9uYW1lIjoiQ3JlZGl0IFJlcGFpciBCdXNpbmVzcyIsImZpcnN0X25hbWUiOiJBdHRhY2ggUGRmIiwibGFzdF9uYW1lIjoiVGVzdGluZyIsImFkbWluX2VtYWlsIjoicGRmQHlvcG1haWwuY29tIiwidXNlcl9pZCI6NDIzNjk2LCJyZWdfaWQiOjEwMDI3MTMsImJpbGxpbmdfcmVmX2lkIjoiM2Y3ZDBkZGYtZjA1Ny00OTZiLWI0OWMtZjAxZTA1ZGU5ODcyIiwidXNlcl90eXBlIjoiYWRtaW4iLCJhY2NvdW50X3N0YXR1cyI6ImFjdGl2ZSIsInJlY3VybHlfcGF5bWVudF9zdGF0dXMiOiJwYWlkIiwiY291bnRyeV9jb2RlIjoyMjQsImNvdW50cnlfbmFtZSI6IlVuaXRlZCBTdGF0ZXMiLCJ0d29fZGlnaXRfY291bnRyeV9jb2RlIjoiVVMiLCJjdXJyZW5jeV9jb2RlIjoiVVNEIiwiY3VycmVuY3lfc3ltYm9sIjoiJCIsInRpbWV6b25lIjoiQW1lcmljYS9Mb3NfQW5nZWxlcyIsImlzX2Vhcmx5X2FjY2VzcyI6MSwiaXNfcHJlX2xhdW5jaCI6ZmFsc2UsImNoYXJnZWJlZV9lbnJvbGxlZCI6ZmFsc2UsImNoYXJnZWJlZV9lbmFibGVkIjpmYWxzZSwiY3JjX2JpbGxpbmdfZW5hYmxlZCI6dHJ1ZSwiaWF0IjoxNzgwMDI3ODIxLCJuYmYiOjE3ODAwMjc4MjEsImV4cCI6MTc4MDExNDIyMSwicGxhbl9uYW1lIjoiU3RhcnQiLCJwdXJjaGFzZWRfbWFzdGVyY2xhc3MiOiJubyIsImlzX3NpZ25lZCI6dHJ1ZSwic2lnbnVwX3N0YXR1cyI6ImNvbXBsZXRlIn0.jD1TDBrRichZ4WwqKaBE5aQtfDL6lVe_0mdbzdMV2pKDpU7zdTPhzMH_8o9SNUA_SlQjDmy-OJ2lZhxHjo69wOKSGaVMrCF1c3MLgIxBxQ_TgXGcDWltbMrKHKBYahIrgjcRHFEbr_Pn4J2YU_N3LFf0hqf6gBCARgltZLLvn5hXjmmRcK-9SJ1R6ldJj4c3S-Mub22iXA7TKoJLoepviS6SAQGVI877_f744KbZchaW3io6hWxKjYhkfRcEQifjsV8gttaSpo8TOi-WwFxiGeEugqxOdKKcCr8pw09XXtjfA0ZhHzgjvj3uAh5IVBqcF59uADhAyQzLii2pfCej5A"

HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}


def test_collect_ai_letter_ids_pages_1_to_7(request_context):
    """
    Iterate pages 1..7 of the library endpoint and collect every
    item.id where isAILetter == True into a single list, and also
    group eligible ids by category_name.
    """
    ai_letter_ids: list = []
    ids_by_category: dict[str, list] = {}

    for page in range(START_PAGE, END_PAGE + 1):
        url = f"{LIBRARY_URL}?page={page}&limit={PAGE_LIMIT}"
        response = request_context.get(url, headers=HEADERS)
        assert response.status == 200, (
            f"GET {url} failed: {response.status} {response.status_text}"
        )

        items = response.json()["list"]

        page_ids = [item["id"] for item in items if item.get("isAILetter")]

        for item in items:
            if item.get("isAILetter"):
                category = item.get("category_name") or "Uncategorized"
                ids_by_category.setdefault(category, []).append(item["id"])

        print(f"Page {page}: total items={len(items)}, AI letter ids={page_ids}")
        ai_letter_ids.extend(page_ids)

    print(f"\nTotal AI letter ids collected (pages {START_PAGE}-{END_PAGE}): "
          f"{len(ai_letter_ids)}")
    print(f"AI letter ids: {ai_letter_ids}")
    print(f"len(ai_letter_ids): {len(ai_letter_ids)}")

    print("\nEligible AI letter ids grouped by category_name:")
    for category, ids in ids_by_category.items():
        print(f"  {category} (count={len(ids)}): {ids}")




"""AI letter ids: [1, 2, 5001, 124, 123, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 26, 27, 125, 135, 126, 136, 127, 128, 121, 28, 29, 30, 33, 34, 36, 40, 42, 43, 44, 47, 49, 51, 56, 57, 58, 59, 62, 63, 64, 65, 66, 68, 69, 70, 72, 73, 74, 76, 129, 130, 131, 132, 122, 78, 89, 106, 109, 114, 115, 116, 117, 120]
len(ai_letter_ids): 75

Eligible AI letter ids grouped by category_name:
  Default (count=2): [1, 2]
  Credit Bureau Letters (count=29): [5001, 124, 123, 3, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 19, 20, 21, 23, 24, 26, 27, 125, 135, 126, 136, 127, 128]
  Creditor Letters (count=34): [121, 28, 29, 30, 33, 34, 36, 40, 42, 43, 44, 47, 49, 51, 56, 57, 58, 59, 62, 63, 64, 65, 66, 68, 69, 70, 72, 73, 74, 76, 129, 130, 131, 132]
  Collection Letters (count=5): [122, 78, 89, 106, 109]
  Misc. Letters (count=5): [114, 115, 116, 117, 120]"""
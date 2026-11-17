"""
Practice: GET request to reqres.in
"""

from urllib import response


BASE_URL = "https://restful-booker.herokuapp.com/"


def test_get_users(api_request):
    payload = {"username": "admin", "password": "password123"}
    response = api_request.post(
        BASE_URL + "auth",
        headers={"Content-Type": "application/json"}, data=payload)
        
    data = response.json()
    token = data.get("token")

    print(f"\nToken: {token}")

    assert response.ok
    assert response.status == 200
    assert "token" in data
    assert len(token) > 0
    assert type(token) == str

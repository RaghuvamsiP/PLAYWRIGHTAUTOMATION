from datetime import datetime

from faker import Faker

faker = Faker()


def _build_client_payload(first_name: str, last_name: str, run_id: int, index: int = 1) -> dict:
    """Build the client payload for the clients API."""
    email = f"{first_name}.{last_name}".lower().replace(" ", "")
    email = f"{email}.{run_id}{index}@yopmail.com"
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "client_status": "1",
        "start_date": datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
        "assigned_to": [1],
        "portal_access": "on",
        "agreement": "no",
        "portal_language": "en",
        "has_email": "0",
        "sendlogininfo": True,
    }


def create_unique_client_payload(run_id: int | None = None, index: int = 1) -> dict:
    """Create a single unique client payload with Faker-generated names."""
    if run_id is None:
        run_id = int(datetime.now().timestamp())
    first_name = faker.first_name()
    last_name = faker.last_name()
    return _build_client_payload(first_name, last_name, run_id, index)


def create_custom_client_payload(run_id: int | None = None, index: int = 1) -> dict:
    """Create a client payload with fixed names."""
    if run_id is None:
        run_id = int(datetime.now().timestamp())
    return _build_client_payload("Delinquent 1", "Primary", run_id, index)


def create_unique_client(auth_api, run_id: int | None = None, index: int = 1):
    """Create a unique client via the API and return the HTTP response."""
    payload = create_unique_client_payload(run_id=run_id, index=index)
    response = auth_api.post("/api/clients", data=payload)
    assert response.ok, response.text()
    return response


def create_custom_client(auth_api, run_id: int | None = None, index: int = 1):
    """Create a custom client via the API and return the HTTP response."""
    payload = create_custom_client_payload(run_id=run_id, index=index)
    response = auth_api.post("/api/clients", data=payload)
    assert response.ok, response.text()
    return response

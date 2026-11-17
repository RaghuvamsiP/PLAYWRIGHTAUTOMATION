from datetime import datetime

from faker import Faker

faker = Faker()


def _build_client_payload(index: int, run_id: int, first_name: str, last_name: str) -> dict:
    """Build a base client payload for the Clients API."""
    email = f"{first_name}.{last_name}".lower().replace(" ", "")
    email = f"{email}.{run_id}{index}@yopmail.com"
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "client_status": "1",
        "start_date": datetime.now().strftime("%m/%d/%Y"),
        "assigned_to": [1],
        "portal_access": "on",
        "agreement": "no",
        "portal_language": "en",
        "has_email": "0",
        "sendlogininfo": True,
    }


def custom_client_payload(run_id: int | None = None, index: int = 1) -> dict:
    """Build a custom client payload with fixed names. Defaults to a single client."""
    if run_id is None:
        run_id = int(datetime.now().timestamp())
    return _build_client_payload(index, run_id, "Search", "Client")


def unique_client_payload(run_id: int | None = None, index: int = 1) -> dict:
    """Build a unique client payload with Faker-generated names. Defaults to a single client."""
    if run_id is None:
        run_id = int(datetime.now().timestamp())
    first_name = faker.first_name()
    last_name = faker.last_name()
    return _build_client_payload(index, run_id, first_name, last_name)
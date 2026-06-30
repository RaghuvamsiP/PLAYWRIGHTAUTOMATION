"""Request payload for the Create Client endpoint (POST /api/clients).

Only last_name and email are randomized (via Faker) per call; every other
field is kept static.
"""

from faker import Faker

fake = Faker("en_US")


def build_create_client_payload() -> dict:
    """Return a fresh create-client payload with a unique last_name + email."""
    last_name = fake.last_name()
    email = f"{fake.unique.user_name()}@yopmail.com"

    return {
        "first_name": "Rate Limit",
        "last_name": last_name,
        "email": email,
        "address": "123  William St",
        "city": "New York",
        "state": "New York",
        "postcode": "10038",
        "client_status": "1",
        "start_date": "06/15/2026",
        "assigned_to": [1],
        "portal_access": "on",
        "agreement": "no",
        "portal_language": "en",
        "has_email": "0",
        "sendlogininfo": True,
    }

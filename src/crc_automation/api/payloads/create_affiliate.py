"""Request payload for the Create Affiliate endpoint (POST /api/affiliates).

Only last_name and email are randomized (via Faker) per call; every other
field is kept static.
"""

from faker import Faker

fake = Faker("en_US")


def build_create_affiliate_payload() -> dict:
    """Return a fresh create-affiliate payload with a unique last_name + email."""
    last_name = fake.last_name()
    email = f"{fake.unique.user_name()}@yopmail.com"

    return {
        "first_name": "Rate Limit",
        "last_name": last_name,
        "status": "1",
        "company_name": "CRC RL Test",
        "mailing_address": "123  William St",
        "city": "New York",
        "state": "New York",
        "zip_code": "10038",
        "email": email,
        "phone": "(088) 888-8888",
        "notes": "smaple notes",
        "portal_access": "on",
        "assigned_to": [1],
    }

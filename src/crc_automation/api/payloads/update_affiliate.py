"""Request payload for the Update Affiliate endpoint (PUT /api/affiliates/{id}).

Only last_name and phone are randomized (via Faker) per call; every other
field is kept static.
"""

from faker import Faker

fake = Faker("en_US")


def build_update_affiliate_payload() -> dict:
    """Return a fresh update-affiliate payload with a new last_name + phone."""
    last_name = fake.last_name()
    phone = fake.numerify("(###) ###-####")

    return {
        "first_name": "Rate Limit",
        "last_name": last_name,
        "status": "1",
        "company_name": "CRC RL Test",
        "mailing_address": "123  William St",
        "city": "New York",
        "state": "New York",
        "zip_code": "10038",
        "email": "rltestou@yopmail.com",
        "phone": phone,
        "notes": "smaple notes",
        "portal_access": "on",
        "assigned_to": [],
    }

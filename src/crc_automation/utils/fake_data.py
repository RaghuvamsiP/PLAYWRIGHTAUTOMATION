"""
Faker-based test data generator for affiliate and client tests.
Name prefixes: A = Active, I = Inactive, P = Pending.
"""

from faker import Faker

fake = Faker("en_US")


def affiliate_data(status: str = "Active") -> dict:
    """Generate fake affiliate data with name prefix based on status.

    Prefix rules:
        Active   -> name starts with 'A'
        Inactive -> name starts with 'I'
        Pending  -> name starts with 'P'
    """
    prefix_map = {
        "Active": "A",
        "Inactive": "I",
        "Pending": "P",
    }
    prefix = prefix_map.get(status, "A")

    first = f"{prefix}{fake.first_name()}"
    last = fake.last_name()
    ts = fake.unique.random_int(min=1000, max=99999)

    return {
        "first_name": first,
        "last_name": last,
        "email": f"{first.lower()}.{last.lower()}{ts}@yopmail.com",
        "phone": fake.numerify("##########"),
        "mobile": fake.numerify("##########"),
        "company": fake.company(),
        "website": fake.url(),
        "fax": fake.numerify("##########"),
        "phone_ext": fake.numerify("###"),
        "address": fake.street_address(),
        "city": fake.city(),
        "state": "California",
        "zip_code": fake.zipcode(),
    }


def unique_email(prefix: str = "autotest") -> str:
    ts = fake.unique.random_int(min=10000, max=99999)
    return f"{prefix}_{ts}@yopmail.com"

import time

from tests.API.helpers.client_payload import custom_client_payload, unique_client_payload

CLIENT_COUNT = 1  # change this to create more clients in test_create_n_clients


def test_create_n_clients(auth_api):
    """Create n clients via the CRC clients API and print client ids from the response."""
    run_id = int(time.time())
    created_ids = []
    failures = []

    for i in range(1, CLIENT_COUNT + 1):
        payload = custom_client_payload(i, run_id)
        response = auth_api.post("/api/clients", data=payload)

        if response.status in (200, 201):
            client_id = response.json()["details"]["id"]
            created_ids.append(client_id)
            print(f"[{i}/{CLIENT_COUNT}] {payload['first_name']} {payload['last_name']} "
                  f"({payload['email']}) -> client_id={client_id}")
        else:
            failures.append((payload["email"], response.status, response.text()))
            print(f"[{i}/{CLIENT_COUNT}] FAILED: email={payload['email']}  "
                  f"status={response.status}  body={response.text()[:200]}")

    print("\n=== Client IDs ===")
    for cid in created_ids:
        print(cid)

    assert not failures, f"{len(failures)} client(s) failed to create: {failures}"
    assert len(created_ids) == CLIENT_COUNT


def test_create_n_unique_clients(auth_api):
    """Create n clients using the unique payload helper."""
    run_id = int(time.time())
    created_ids = []
    failures = []

    for i in range(1, CLIENT_COUNT + 1):
        payload = unique_client_payload(i, run_id)
        response = auth_api.post("/api/clients", data=payload)

        if response.status in (200, 201):
            client_id = response.json()["details"]["id"]
            created_ids.append(client_id)
            print(f"[{i}/{CLIENT_COUNT}] {payload['first_name']} {payload['last_name']} "
                  f"({payload['email']}) -> client_id={client_id}")
        else:
            failures.append((payload["email"], response.status, response.text()))
            print(f"[{i}/{CLIENT_COUNT}] FAILED: email={payload['email']}  "
                  f"status={response.status}  body={response.text()[:200]}")

    print("\n=== Client IDs (unique payload) ===")
    for cid in created_ids:
        print(cid)

    assert not failures, f"{len(failures)} client(s) failed to create: {failures}"
    assert len(created_ids) == CLIENT_COUNT


def test_delete_clients(auth_api):
    """Delete clients with ids 100..200 (inclusive). 2xx and 404 are both acceptable."""
    deleted = []
    not_found = []
    failures = []

    for client_id in range(100, 201):
        response = auth_api.delete(f"/api/clients/{client_id}")

        if 200 <= response.status < 300:
            deleted.append(client_id)
            print(f"Deleted client_id={client_id}  status={response.status}")
        elif response.status == 404:
            not_found.append(client_id)
            print(f"Not found  client_id={client_id}")
        else:
            failures.append((client_id, response.status, response.text()[:200]))
            print(f"FAILED client_id={client_id}  status={response.status}  "
                  f"body={response.text()[:200]}")

    print(f"\nSummary: deleted={len(deleted)}  not_found={len(not_found)}  failed={len(failures)}")
    print(f"Deleted ids: {deleted}")

    assert not failures, f"{len(failures)} delete(s) failed: {failures}"

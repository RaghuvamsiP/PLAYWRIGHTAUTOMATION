from crc_automation.api.clients.create_client import create_unique_client
from crc_automation.api.report_providers import (
	CREDIT_HERO_SCORE,
	PROVIDER_2,
	PROVIDER_3,
	PROVIDER_4,
	PROVIDER_5,
	PROVIDER_6,
)


SELECTED_PROVIDER = CREDIT_HERO_SCORE


def test_report_import(auth_api, company_id):
	"""Create a client, grant credit access, request a report, then fetch it."""
	create_response = create_unique_client(auth_api)
	client_id = create_response.json()["details"]["id"]

	provider = SELECTED_PROVIDER
	process_payload = provider["process"].copy()
	process_payload["clientId"] = client_id
	process_payload["croId"] = company_id
	process_response = auth_api.post(
		"/api/report/process",
		data=process_payload,
	)
	assert process_response.ok, process_response.text()
	process_body = process_response.json()
	assert process_body["status"] == "success"
	request_id = process_body["data"]["requestId"]

	credit_access_payload = provider["credit_access"].copy()
	credit_access_response = auth_api.put(
		f"/api/clients/{client_id}/credit-access",
		data=credit_access_payload,
	)
	assert credit_access_response.ok, credit_access_response.text()
	assert credit_access_response.json()["status"] == "success"

	fetch_payload = provider["fetch"].copy()
	fetch_payload["clientId"] = client_id
	fetch_payload["requestId"] = request_id

	fetch_response = auth_api.post(provider["fetch"]["path"], data=fetch_payload)
	assert fetch_response.ok, fetch_response.text()

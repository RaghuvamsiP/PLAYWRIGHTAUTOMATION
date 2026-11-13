"""
Mail Service Types API Tests
GET: /api/service/types

Positive Tests:
1) Verify status code is 200
2) Verify response status is "success"
3) Verify response message
4) Verify services list is not empty
5) Verify "First Class Mail" exists in services
6) Verify "Certified Mail" exists in services
7) Verify each service has a "name" field
8) Verify services count is 2

Negative Tests:
9) Verify POST method is not allowed
10) Verify PUT method is not allowed
11) Verify DELETE method is not allowed
12) Verify invalid endpoint returns error
"""

base_url = "http://qa-cloudmail-letters.internal.creditrepaircloud.com/api"
endpoint = f"{base_url}/service/types"


# -------------------------------------------------------------------
# Positive Tests
# -------------------------------------------------------------------
def test_status_code_is_200(request_context):
    """Verify GET /service/types returns 200"""
    response = request_context.get(endpoint)
    assert response.status == 200


def test_response_status_is_success(request_context):
    """Verify response status is 'success'"""
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    assert data['status'] == 'success'


def test_response_message(request_context):
    """Verify response message"""
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    assert data['message'] == 'Mail service types retrieved successfully.'


def test_services_list_is_not_empty(request_context):
    """Verify services list is not empty"""
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    assert len(data['data']['services']) > 0


def test_first_class_mail_exists(request_context):
    """Verify 'First Class Mail' exists in services"""
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    service_names = [s['name'] for s in data['data']['services']]
    assert 'First Class Mail' in service_names


def test_certified_mail_exists(request_context):
    """Verify 'Certified Mail' exists in services"""
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    service_names = [s['name'] for s in data['data']['services']]
    assert 'Certified Mail' in service_names


def test_each_service_has_name_field(request_context):
    """Verify each service object has a 'name' field"""
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    for service in data['data']['services']:
        assert 'name' in service


def test_services_count(request_context):
    """Verify services count is 2"""
    response = request_context.get(endpoint)
    assert response.status == 200

    data = response.json()
    assert len(data['data']['services']) == 2


# -------------------------------------------------------------------
# Negative Tests
# -------------------------------------------------------------------
def test_post_method_not_allowed(request_context):
    """Verify POST method returns 405"""
    response = request_context.post(endpoint)
    assert response.status == 405


def test_put_method_not_allowed(request_context):
    """Verify PUT method returns 405"""
    response = request_context.put(endpoint)
    assert response.status == 405


def test_delete_method_not_allowed(request_context):
    """Verify DELETE method returns 405"""
    response = request_context.delete(endpoint)
    assert response.status == 405


def test_invalid_endpoint_returns_error(request_context):
    """Verify invalid endpoint returns 404"""
    response = request_context.get(f"{base_url}/service/invalid")
    assert response.status == 404

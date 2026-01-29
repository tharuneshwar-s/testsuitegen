import pytest
import requests
from typing import Dict, Any, Optional
import uuid

BASE_URL = "http://localhost:8003/"
ENDPOINT = "/users/profile"
METHOD = "POST"

# Operation: create_user_profile_users_profile_post
# Error Codes Expected: 422


@pytest.fixture(scope="module")
def api_client():
    '''Provides a configured API client for testing.'''
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="class")
def test_data_setup(api_client):
    '''
    Setup fixture that creates test data before tests and cleans up after.
    This ensures each test run has a clean state.
    '''
    created_resources = []
    
    # Setup: Create any prerequisite test data here
    # Example: If testing user operations, create test users
    
    
    yield {"created_resources": created_resources}
    
    # Teardown: Clean up all created resources
    for resource in created_resources:
        try:
            api_client.delete(resource["endpoint"])
        except Exception as e:
            print(f"Cleanup warning: Could not delete {resource['type']} {resource['id']}: {e}")


class TestCreate_user_profile_users_profile_post:
    '''Test suite for POST /users/profile endpoint.'''
    
    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, test_data_setup):
        '''Automatically inject test data setup for each test method.'''
        self.test_data = test_data_setup
        yield
        # Per-test cleanup can go here if needed

    @pytest.mark.parametrize("intent, payload, path_params, expected_status", [
        pytest.param(
            "HAPPY_PATH",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            201,
            id="HAPPY_PATH"
        ),
        pytest.param(
            "REQUIRED_FIELD_MISSING",
            {'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            400,
            id="REQUIRED_FIELD_MISSING"
        ),
        pytest.param(
            "REQUIRED_FIELD_MISSING",
            {'username': 'alice.smith', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            400,
            id="REQUIRED_FIELD_MISSING"
        ),
        pytest.param(
            "REQUIRED_FIELD_MISSING",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            400,
            id="REQUIRED_FIELD_MISSING"
        ),
        pytest.param(
            "BOUNDARY_MIN_LENGTH_MINUS_ONE",
            {'username': 'xx', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="BOUNDARY_MIN_LENGTH_MINUS_ONE"
        ),
        pytest.param(
            "BOUNDARY_MAX_LENGTH_PLUS_ONE",
            {'username': 'xxxxxxxxxxxxxxxxxxxxx', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="BOUNDARY_MAX_LENGTH_PLUS_ONE"
        ),
        pytest.param(
            "PATTERN_MISMATCH",
            {'username': '!!!invalid_pattern!!!', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="PATTERN_MISMATCH"
        ),
        pytest.param(
            "FORMAT_INVALID",
            {'username': 'alice.smith', 'email': 'invalid_format_value', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="FORMAT_INVALID"
        ),
        pytest.param(
            "SQL_INJECTION",
            {'username': 'alice.smith', 'email': "' OR '1'='1", 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="SQL_INJECTION"
        ),
        pytest.param(
            "XSS_INJECTION",
            {'username': 'alice.smith', 'email': '<script>alert(1)</script>', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="XSS_INJECTION"
        ),
        pytest.param(
            "WHITESPACE_ONLY",
            {'username': 'alice.smith', 'email': '   ', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="WHITESPACE_ONLY"
        ),
        pytest.param(
            "BOUNDARY_MIN_LENGTH_MINUS_ONE",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': '', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="BOUNDARY_MIN_LENGTH_MINUS_ONE"
        ),
        pytest.param(
            "BOUNDARY_MAX_LENGTH_PLUS_ONE",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="BOUNDARY_MAX_LENGTH_PLUS_ONE"
        ),
        pytest.param(
            "SQL_INJECTION",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': "' OR '1'='1", 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="SQL_INJECTION"
        ),
        pytest.param(
            "XSS_INJECTION",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': '<script>alert(1)</script>', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="XSS_INJECTION"
        ),
        pytest.param(
            "WHITESPACE_ONLY",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': '   ', 'bio': 'A software engineer with over 10 years of experience.', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="WHITESPACE_ONLY"
        ),
        pytest.param(
            "BOUNDARY_MAX_LENGTH_PLUS_ONE",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="BOUNDARY_MAX_LENGTH_PLUS_ONE"
        ),
        pytest.param(
            "SQL_INJECTION",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': "' OR '1'='1", 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="SQL_INJECTION"
        ),
        pytest.param(
            "XSS_INJECTION",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': '<script>alert(1)</script>', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="XSS_INJECTION"
        ),
        pytest.param(
            "WHITESPACE_ONLY",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': '   ', 'website': 'https://www.alicesmith.com'},
            {},
            422,
            id="WHITESPACE_ONLY"
        ),
        pytest.param(
            "PATTERN_MISMATCH",
            {'username': 'alice.smith', 'email': 'alice.smith@domain.com', 'full_name': 'Alice Smith', 'bio': 'A software engineer with over 10 years of experience.', 'website': '!!!invalid_pattern!!!'},
            {},
            422,
            id="PATTERN_MISMATCH"
        ),
    ])
    def test_create_user_profile_users_profile_post_contract(self, api_client, intent, payload, path_params, expected_status):
        """
        Validates POST /users/profile against the OpenAPI contract.
        Intent: {intent}
        Expected Status: {expected_status}
        
        
        Error Response Information:
        - Status 422: Validation Error
          Response Schema: object with properties: detail
        
        """
        url = f"{BASE_URL}{ENDPOINT}"
        
        # Replace path parameters with test data if available
        if path_params:
            for param_name, param_value in path_params.items():
                # Use created test resource ID if available and param_value is not set
                if param_value is None and hasattr(self, 'test_data') and self.test_data.get('created_resources'):
                    for resource in self.test_data['created_resources']:
                        param_value = resource.get('id', 1)
                        break
                # Handle INVALID_TYPE for path parameters
                if param_value == "__INVALID_TYPE__":
                    param_value = "invalid_string_value"
                url = url.replace(f"{{{param_name}}}", str(param_value))
        
        # Handle any remaining unreplaced path parameters (use test data)
        if "{" in url and hasattr(self, 'test_data') and self.test_data.get('created_resources'):
            for resource in self.test_data['created_resources']:
                # Replace any remaining path parameters with the resource ID
                import re
                url = re.sub(r'\{\w+\}', str(resource.get('id', 1)), url)
                break
        
        # Extract query parameters from payload
        query_params = {}
        if payload and METHOD in ("GET", "DELETE"):
            # For GET/DELETE, move payload to query params
            query_params = payload.copy()
            payload = None
        
        # Generate unique data for creation tests to avoid conflicts
        if METHOD in ("POST", "PUT", "PATCH") and payload and intent == "HAPPY_PATH":
            if "username" in payload:
                payload["username"] = f"{payload['username']}_{uuid.uuid4().hex[:8]}"
            if "email" in payload:
                email_parts = payload["email"].split("@")
                payload["email"] = f"{email_parts[0]}_{uuid.uuid4().hex[:8]}@{email_parts[1]}"
        
        
        response = api_client.request(
            method=METHOD,
            url=url,
            json=payload if payload else None,
            params=query_params if query_params else None,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == expected_status,             f"Failed Intent: {intent}. Expected {expected_status}, got {response.status_code}. Body: {response.text}"
        
        # Store created resource for cleanup if this is a creation test
        if response.status_code in (200, 201) and METHOD == "POST" and hasattr(self, 'test_data'):
            try:
                resource_data = response.json()
                if resource_data.get("id"):
                    self.test_data['created_resources'].append({
                        "type": "test_resource",
                        "id": resource_data["id"],
                        "endpoint": f"{url}/{resource_data['id']}"
                    })
            except Exception:
                pass
        
        
        # Validate error response structure if applicable
        if expected_status >= 400 and response.content:
            try:
                error_body = response.json()
                assert error_body is not None, "Error response should have a JSON body"
                # Additional validation can be added here based on error schema
            except ValueError:
                # Some error responses might not have JSON body
                pass
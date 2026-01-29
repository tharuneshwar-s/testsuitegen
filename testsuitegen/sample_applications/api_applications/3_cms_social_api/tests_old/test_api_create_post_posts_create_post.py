import pytest
import requests
from typing import Dict, Any, Optional
import uuid

BASE_URL = "http://localhost:8003/"
ENDPOINT = "/posts/create"
METHOD = "POST"

# Operation: create_post_posts_create_post
# Error Codes Expected: 422


@pytest.fixture(scope="module")
def api_client():
    """Provides a configured API client for testing."""
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="class")
def test_data_setup(api_client):
    """
    Setup fixture that creates test data before tests and cleans up after.
    This ensures each test run has a clean state.
    """
    created_resources = []

    # Setup: Create any prerequisite test data here
    # Example: If testing user operations, create test users

    yield {"created_resources": created_resources}

    # Teardown: Clean up all created resources
    for resource in created_resources:
        try:
            api_client.delete(resource["endpoint"])
        except Exception as e:
            print(
                f"Cleanup warning: Could not delete {resource['type']} {resource['id']}: {e}"
            )


class TestCreate_post_posts_create_post:
    """Test suite for POST /posts/create endpoint."""

    @pytest.fixture(autouse=True)
    def setup_method_fixture(self, test_data_setup):
        """Automatically inject test data setup for each test method."""
        self.test_data = test_data_setup
        yield
        # Per-test cleanup can go here if needed

    @pytest.mark.parametrize(
        "intent, payload, path_params, expected_status",
        [
            pytest.param(
                "HAPPY_PATH",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                201,
                id="HAPPY_PATH",
            ),
            pytest.param(
                "REQUIRED_FIELD_MISSING",
                {
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                400,
                id="REQUIRED_FIELD_MISSING",
            ),
            pytest.param(
                "REQUIRED_FIELD_MISSING",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                400,
                id="REQUIRED_FIELD_MISSING",
            ),
            pytest.param(
                "REQUIRED_FIELD_MISSING",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                400,
                id="REQUIRED_FIELD_MISSING",
            ),
            pytest.param(
                "REQUIRED_FIELD_MISSING",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                400,
                id="REQUIRED_FIELD_MISSING",
            ),
            pytest.param(
                "BOUNDARY_MIN_LENGTH_MINUS_ONE",
                {
                    "title": "xxxx",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="BOUNDARY_MIN_LENGTH_MINUS_ONE",
            ),
            pytest.param(
                "BOUNDARY_MAX_LENGTH_PLUS_ONE",
                {
                    "title": "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="BOUNDARY_MAX_LENGTH_PLUS_ONE",
            ),
            pytest.param(
                "SQL_INJECTION",
                {
                    "title": "' OR '1'='1",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="SQL_INJECTION",
            ),
            pytest.param(
                "XSS_INJECTION",
                {
                    "title": "<script>alert(1)</script>",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="XSS_INJECTION",
            ),
            pytest.param(
                "WHITESPACE_ONLY",
                {
                    "title": "   ",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="WHITESPACE_ONLY",
            ),
            pytest.param(
                "BOUNDARY_MIN_LENGTH_MINUS_ONE",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "xxxxxxxxx",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="BOUNDARY_MIN_LENGTH_MINUS_ONE",
            ),
            pytest.param(
                "SQL_INJECTION",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "' OR '1'='1",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="SQL_INJECTION",
            ),
            pytest.param(
                "XSS_INJECTION",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "<script>alert(1)</script>",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="XSS_INJECTION",
            ),
            pytest.param(
                "WHITESPACE_ONLY",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "   ",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="WHITESPACE_ONLY",
            ),
            pytest.param(
                "ENUM_MISMATCH",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "INVALID_ENUM_VALUE",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "__PLACEHOLDER_STRING_category__",
                },
                {},
                422,
                id="ENUM_MISMATCH",
            ),
            pytest.param(
                "SQL_INJECTION",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "' OR '1'='1",
                },
                {},
                422,
                id="SQL_INJECTION",
            ),
            pytest.param(
                "XSS_INJECTION",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "<script>alert(1)</script>",
                },
                {},
                422,
                id="XSS_INJECTION",
            ),
            pytest.param(
                "WHITESPACE_ONLY",
                {
                    "title": "__PLACEHOLDER_STRING_title__",
                    "content": "__PLACEHOLDER_STRING_content__",
                    "status": "DRAFT",
                    "tags": ["__PLACEHOLDER_STRING_None__"],
                    "category": "   ",
                },
                {},
                422,
                id="WHITESPACE_ONLY",
            ),
        ],
    )
    def test_create_post_posts_create_post_contract(
        self, api_client, intent, payload, path_params, expected_status
    ):
        """
        Validates POST /posts/create against the OpenAPI contract.
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
                if (
                    param_value is None
                    and hasattr(self, "test_data")
                    and self.test_data.get("created_resources")
                ):
                    for resource in self.test_data["created_resources"]:
                        param_value = resource.get("id", 1)
                        break
                # Handle INVALID_TYPE for path parameters
                if param_value == "__INVALID_TYPE__":
                    param_value = "invalid_string_value"
                url = url.replace(f"{{{param_name}}}", str(param_value))

        # Handle any remaining unreplaced path parameters (use test data)
        if (
            "{" in url
            and hasattr(self, "test_data")
            and self.test_data.get("created_resources")
        ):
            for resource in self.test_data["created_resources"]:
                # Replace any remaining path parameters with the resource ID
                import re

                url = re.sub(r"\{\w+\}", str(resource.get("id", 1)), url)
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
                payload["email"] = (
                    f"{email_parts[0]}_{uuid.uuid4().hex[:8]}@{email_parts[1]}"
                )

        response = api_client.request(
            method=METHOD,
            url=url,
            json=payload if payload else None,
            params=query_params if query_params else None,
            headers={"Content-Type": "application/json"},
        )

        assert (
            response.status_code == expected_status
        ), f"Failed Intent: {intent}. Expected {expected_status}, got {response.status_code}. Body: {response.text}"

        # Store created resource for cleanup if this is a creation test
        if (
            response.status_code in (200, 201)
            and METHOD == "POST"
            and hasattr(self, "test_data")
        ):
            try:
                resource_data = response.json()
                if resource_data.get("id"):
                    self.test_data["created_resources"].append(
                        {
                            "type": "test_resource",
                            "id": resource_data["id"],
                            "endpoint": f"{url}/{resource_data['id']}",
                        }
                    )
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

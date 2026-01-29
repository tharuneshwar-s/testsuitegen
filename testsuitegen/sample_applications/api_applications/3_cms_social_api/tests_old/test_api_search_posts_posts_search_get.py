import pytest
import requests
from typing import Dict, Any, Optional
import uuid

BASE_URL = "http://localhost:8003/"
ENDPOINT = "/posts/search"
METHOD = "GET"

# Operation: search_posts_posts_search_get
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


class TestSearch_posts_posts_search_get:
    """Test suite for GET /posts/search endpoint."""

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
                {"q": "__PLACEHOLDER_STRING_q__"},
                {},
                200,
                id="HAPPY_PATH",
            ),
            pytest.param(
                "REQUIRED_FIELD_MISSING", {}, {}, 400, id="REQUIRED_FIELD_MISSING"
            ),
        ],
    )
    def test_search_posts_posts_search_get_contract(
        self, api_client, intent, payload, path_params, expected_status
    ):
        """
        Validates GET /posts/search against the OpenAPI contract.
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

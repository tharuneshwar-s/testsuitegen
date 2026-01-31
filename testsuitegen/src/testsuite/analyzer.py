"""
Static Test Analyzer Module

Analyzes IR and payloads to determine which tests require prerequisite resources.
This is deterministic - no LLM involved.
"""

from typing import List, Dict, Any, Set
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class ResourceRequirement:
    """Represents a resource that must be created before a test can run."""

    resource_type: str  # e.g., "user", "transfer", "product"
    endpoint: str  # POST endpoint to create the resource (e.g., "/users")
    param_name: str  # The path parameter that needs this resource (e.g., "user_id")
    schema: Dict[str, Any] = field(
        default_factory=dict
    )  # Schema for creating the resource
    required_fields: List[str] = field(default_factory=list)
    id_field: str = "id"  # Field name in response containing the resource ID


@dataclass
class TestAnalysis:
    """Analysis result for a single operation's tests."""

    operation_id: str
    method: str
    path: str
    needs_setup: bool
    resource_requirements: List[ResourceRequirement] = field(default_factory=list)
    create_operations: Dict[str, Dict] = field(
        default_factory=dict
    )  # Maps resource_type to create operation details


class StaticTestAnalyzer:
    """
    Analyzes the IR to determine which tests need prerequisite resource creation.

    Rules:
    1. GET/DELETE with path params -> needs the resource to exist
    2. PUT/PATCH with path params -> needs the resource to exist
    3. POST usually creates, so no prereq needed (unless nested resource)
    """

    def __init__(self, ir: dict, payloads: List[Dict]):
        self.ir = ir
        self.payloads = payloads
        self.ops_map = {op["id"]: op for op in ir.get("operations", [])}
        self._build_create_operations_map()

    def _build_create_operations_map(self) -> None:
        """
        Build a map of resource types to their create operations.
        This helps us know how to create prerequisite resources.
        """
        self.create_ops: Dict[str, Dict] = {}

        for op in self.ir.get("operations", []):
            method = op.get("method", "").upper()
            path = op.get("path", "")

            # POST to a collection endpoint is a create operation
            if method == "POST":
                # Extract resource type from path (e.g., "/users" -> "user", "/transfers" -> "transfer")
                resource_type = self._extract_resource_type(path)
                if resource_type:
                    self.create_ops[resource_type] = {
                        "operation_id": op["id"],
                        "path": path,
                        "method": method,
                        "inputs": op.get("inputs", {}),
                        "schema": self._get_body_schema(op),
                    }

    def _extract_resource_type(self, path: str) -> str:
        """
        Extract resource type from path.
        E.g., "/users" -> "user", "/api/v1/transfers" -> "transfer"
        """
        # Remove leading/trailing slashes and split
        parts = path.strip("/").split("/")

        # Find the last non-parameterized segment
        for part in reversed(parts):
            if not part.startswith("{"):
                # Singularize (basic: remove trailing 's')
                resource = (
                    part.rstrip("s") if part.endswith("s") and len(part) > 1 else part
                )
                return resource
        return ""

    def _get_body_schema(self, op: Dict) -> Dict:
        """Extract body schema from operation."""
        body = op.get("inputs", {}).get("body", {})
        return body.get("schema", {})

    def _get_path_params(self, op: Dict) -> List[Dict]:
        """Get path parameters from operation."""
        return op.get("inputs", {}).get("path", [])

    def _infer_create_endpoint(self, path: str, path_params: List[Dict]) -> str:
        """
        Infer the create endpoint from a GET/DELETE endpoint.
        E.g., "/users/{user_id}" -> "/users"
        """
        # Remove all path parameter placeholders
        result = path
        for param in path_params:
            param_name = param.get("name", "")
            result = result.replace(f"/{{{param_name}}}", "")
        return result if result else "/"

    def _infer_resource_type_from_param(self, param_name: str) -> str:
        """
        Infer resource type from path parameter name.
        E.g., "user_id" -> "user", "transfer_id" -> "transfer"
        """
        if param_name.endswith("_id"):
            return param_name[:-3]
        return param_name

    def analyze_operation(self, operation_id: str) -> TestAnalysis:
        """
        Analyze a single operation to determine if it needs test data setup.
        """
        op = self.ops_map.get(operation_id)
        if not op:
            return TestAnalysis(
                operation_id=operation_id,
                method="",
                path="",
                needs_setup=False,
            )

        method = op.get("method", "").upper()
        path = op.get("path", "")
        path_params = self._get_path_params(op)

        analysis = TestAnalysis(
            operation_id=operation_id,
            method=method,
            path=path,
            needs_setup=False,
            resource_requirements=[],
            create_operations={},
        )

        # Determine if setup is needed
        needs_setup = False

        if method in ("GET", "DELETE", "PUT", "PATCH") and path_params:
            needs_setup = True

            for param in path_params:
                param_name = param.get("name", "")
                resource_type = self._infer_resource_type_from_param(param_name)
                create_endpoint = self._infer_create_endpoint(path, path_params)

                # Find the create operation for this resource type
                create_op = self.create_ops.get(resource_type, {})

                requirement = ResourceRequirement(
                    resource_type=resource_type,
                    endpoint=create_op.get("path", create_endpoint),
                    param_name=param_name,
                    schema=create_op.get("schema", {}),
                    required_fields=self._extract_required_fields(
                        create_op.get("schema", {})
                    ),
                    id_field="id",
                )

                analysis.resource_requirements.append(requirement)

                if create_op:
                    analysis.create_operations[resource_type] = create_op

        analysis.needs_setup = needs_setup
        logger.debug(
            "analyze_operation: %s %s needs_setup=%s resources=%d",
            operation_id,
            path,
            analysis.needs_setup,
            len(analysis.resource_requirements),
        )
        return analysis

    def _extract_required_fields(self, schema: Dict) -> List[str]:
        """Extract required fields from a JSON schema."""
        return schema.get("required", [])

    def analyze_all(self) -> Dict[str, TestAnalysis]:
        """Analyze all operations and return a map of operation_id to analysis."""
        results = {}
        for op_id in self.ops_map.keys():
            results[op_id] = self.analyze_operation(op_id)
        return results

    def get_happy_path_payload(self, operation_id: str) -> Dict:
        """
        Get the HAPPY_PATH payload for an operation.
        This is used to create prerequisite resources.
        """
        for payload in self.payloads:
            if (
                payload.get("operation_id") == operation_id
                and payload.get("intent", "").upper() == "HAPPY_PATH"
            ):
                return payload.get("payload", {})
        return {}

"""
Setup Planner Module

Plans the test data setup based on analysis results.
Determines exactly what resources need to be created and in what order.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from testsuitegen.src.testsuite.analyzer import TestAnalysis, ResourceRequirement


@dataclass
class SetupStep:
    """A single step in the test data setup plan."""

    step_id: int
    action: str  # "create", "update", "custom"
    resource_type: str
    endpoint: str
    method: str  # HTTP method
    payload: Dict[str, Any]
    variable_name: str  # Variable to store the result (e.g., "created_user")
    id_extraction: str  # How to extract ID (e.g., "response.json()['id']")
    depends_on: List[int] = field(default_factory=list)  # Step IDs this depends on


@dataclass
class TeardownStep:
    """A single step in the teardown plan."""

    step_id: int
    endpoint_template: str  # e.g., "/users/{id}"
    variable_name: str  # Variable containing the resource ID


@dataclass
class SetupPlan:
    """Complete setup and teardown plan for a test file."""

    operation_id: str
    needs_setup: bool
    setup_steps: List[SetupStep] = field(default_factory=list)
    teardown_steps: List[TeardownStep] = field(default_factory=list)
    placeholder_mappings: Dict[str, str] = field(
        default_factory=dict
    )  # Maps "USE_CREATED_RESOURCE" -> variable


class SetupPlanner:
    """
    Plans test data setup based on analysis results.

    The planner creates a deterministic, executable plan that the
    Fixture Compiler will turn into actual Python code.
    """

    def __init__(self, payloads: List[Dict]):
        self.payloads = payloads
        self._payload_cache: Dict[str, Dict] = {}
        self._build_payload_cache()

    def _build_payload_cache(self) -> None:
        """Cache HAPPY_PATH payloads by operation_id."""
        for payload in self.payloads:
            op_id = payload.get("operation_id", "")
            intent = payload.get("intent", "").upper()
            if intent == "HAPPY_PATH" and op_id:
                self._payload_cache[op_id] = payload.get("payload", {})

    def plan(
        self, analysis: TestAnalysis, all_analyses: Dict[str, TestAnalysis]
    ) -> SetupPlan:
        """
        Create a setup plan for an operation based on its analysis.

        Args:
            analysis: Analysis result for the operation
            all_analyses: Map of all operation analyses (to find create operations)
        """
        plan = SetupPlan(
            operation_id=analysis.operation_id,
            needs_setup=analysis.needs_setup,
        )

        if not analysis.needs_setup:
            return plan

        step_id = 0

        for requirement in analysis.resource_requirements:
            step_id += 1

            # Find the payload to use for creating this resource
            create_payload = self._find_create_payload(
                requirement, analysis, all_analyses
            )

            # Create the setup step
            setup_step = SetupStep(
                step_id=step_id,
                action="create",
                resource_type=requirement.resource_type,
                endpoint=requirement.endpoint,
                method="POST",
                payload=create_payload,
                variable_name=f"created_{requirement.resource_type}",
                id_extraction=f"response.json()['{requirement.id_field}']",
            )
            plan.setup_steps.append(setup_step)

            # Create the teardown step
            teardown_step = TeardownStep(
                step_id=step_id,
                endpoint_template=f"{requirement.endpoint}/{{{requirement.param_name}}}",
                variable_name=f"created_{requirement.resource_type}_id",
            )
            plan.teardown_steps.append(teardown_step)

            # Map the placeholder to the variable
            plan.placeholder_mappings["USE_CREATED_RESOURCE"] = (
                f"created_{requirement.resource_type}_id"
            )
            plan.placeholder_mappings[
                f"USE_CREATED_RESOURCE_{requirement.resource_type.upper()}"
            ] = f"created_{requirement.resource_type}_id"

        return plan

    def _find_create_payload(
        self,
        requirement: ResourceRequirement,
        analysis: TestAnalysis,
        all_analyses: Dict[str, TestAnalysis],
    ) -> Dict:
        """
        Find the best payload to use for creating a prerequisite resource.

        Priority:
        1. HAPPY_PATH payload from the create operation for this resource type
        2. Inferred minimal payload from schema
        3. Empty dict (last resort)
        """
        # Find the create operation for this resource type
        create_op = analysis.create_operations.get(requirement.resource_type, {})
        if create_op:
            create_op_id = create_op.get("operation_id", "")
            if create_op_id in self._payload_cache:
                return self._payload_cache[create_op_id]

        # Try to find any POST operation to the same endpoint
        for op_id, op_analysis in all_analyses.items():
            if (
                op_analysis.method == "POST"
                and op_analysis.path == requirement.endpoint
            ):
                if op_id in self._payload_cache:
                    return self._payload_cache[op_id]

        # Infer minimal payload from schema
        return self._infer_payload_from_schema(
            requirement.schema, requirement.required_fields
        )

    def _infer_payload_from_schema(
        self, schema: Dict, required_fields: List[str]
    ) -> Dict:
        """
        Infer a minimal valid payload from schema.
        Uses conservative default values.
        """
        payload = {}
        properties = schema.get("properties", {})

        for field_name in required_fields:
            field_schema = properties.get(field_name, {})
            payload[field_name] = self._get_default_value(field_name, field_schema)

        return payload

    def _get_default_value(self, field_name: str, field_schema: Dict) -> Any:
        """Get a sensible default value based on field name and schema."""
        field_type = field_schema.get("type", "string")

        # Common field name patterns
        if "email" in field_name.lower():
            return "test@example.com"
        if "name" in field_name.lower():
            return "Test Resource"
        if "id" in field_name.lower() and field_type == "integer":
            return 10000
        if "amount" in field_name.lower():
            return 100.00
        if "status" in field_name.lower():
            return "active"
        if "description" in field_name.lower():
            return "Test description"

        # Type-based defaults
        if field_type == "string":
            min_len = field_schema.get("minLength", 1)
            return "test" + ("x" * max(0, min_len - 4))
        if field_type == "integer":
            minimum = field_schema.get("minimum", 0)
            maximum = field_schema.get("maximum", 99999)
            return (minimum + maximum) // 2 if maximum else minimum + 1
        if field_type == "number":
            minimum = field_schema.get("minimum", 0)
            maximum = field_schema.get("maximum", 10000)
            return float((minimum + maximum) / 2) if maximum else float(minimum + 1)
        if field_type == "boolean":
            return True
        if field_type == "array":
            return []
        if field_type == "object":
            return {}

        return "test_value"

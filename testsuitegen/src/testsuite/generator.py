import os
import pprint
from collections import defaultdict
from typing import List, Dict
from jinja2 import Template
from testsuitegen.src.llm_enhancer.python_enhancer.test_suite_enhancer.enhancer import (
    enhance_code as enhance_code_python,
)
from testsuitegen.src.llm_enhancer.typescript_enhancer.test_suite_enhancer.enhancer import (
    enhance_code as enhance_code_ts,
)
from testsuitegen.src.testsuite.templates import (
    UNIT_TEST_TEMPLATE,
    API_TEST_TEMPLATE,
    OPENAPI_JEST_TEST_TEMPLATE,
    TYPESCRIPT_FUNCTION_TEST_TEMPLATE,
)
from testsuitegen.src.testsuite.analyzer import StaticTestAnalyzer
from testsuitegen.src.testsuite.planner import SetupPlanner
from testsuitegen.src.testsuite.compiler import FixtureCompiler

import logging

logger = logging.getLogger(__name__)


def _format_payload(payload: dict, indent: int = 8) -> str:
    """Format a payload dict for embedding in test code.

    Uses pprint to handle long strings properly with line wrapping.
    """
    formatted = pprint.pformat(payload, width=80, indent=4)
    # Add proper indentation for embedding in test code
    lines = formatted.split("\n")
    indented_lines = [lines[0]] + [" " * indent + line for line in lines[1:]]
    return "\n".join(indented_lines)


class TestSuiteGenerator:
    def __init__(
        self,
        output_dir: str = "generated_tests",
        llm_provider: str = None,
        llm_model: str = None,
    ):
        self.output_dir = output_dir
        self.llm_provider = llm_provider
        self.llm_model = llm_model
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_python_unit_tests(
        self, ir: dict, payloads: List[Dict], module_name: str
    ):
        """
        Generates unit tests for raw Python functions.
        """
        grouped = self._group_by_operation(payloads)

        # Build a map of operation_id -> enum info from IR
        ops_enum_types = self._extract_enum_types_from_ir(ir)
        ops_enum_conversions = self._extract_enum_conversions_from_ir(ir)

        for op_id, cases in grouped.items():
            # Get enum types used by this operation
            enum_types = ops_enum_types.get(op_id, [])
            enum_conversions = ops_enum_conversions.get(op_id, {})

            # Format payloads with enum conversion
            formatted_cases = []
            for case in cases:
                formatted_case = dict(case)
                formatted_case["payload_formatted"] = self._format_payload_with_enums(
                    case.get("payload", {})
                )
                formatted_cases.append(formatted_case)

            # Render with all test cases (Happy Path + Edge Cases)
            template = Template(UNIT_TEST_TEMPLATE)
            code = template.render(
                module_path=module_name,
                function_name=op_id,
                operation_id=op_id,
                test_cases=formatted_cases,  # Pass formatted cases
                enum_types=enum_types,  # Pass enum types for import
                enum_conversions=enum_conversions,  # Pass param->enum_type mapping
            )

            self._write_file("unit", f"test_{op_id}.py", code, test_type="unit")

    def generate_typescript_tests(self, ir: dict, payloads: List[Dict]):
        """
        Generates unit tests for TypeScript functions.
        """
        grouped = self._group_by_operation(payloads)
        # Import path relative to tests/ folder - tests are in tests/ so we need ../src/
        module_path = "../src/validator"

        for op_id, cases in grouped.items():
            template = Template(TYPESCRIPT_FUNCTION_TEST_TEMPLATE)
            code = template.render(
                module_path=module_path,
                function_name=op_id,
                operation_id=op_id,
                test_cases=cases,
            )

            self._write_file(
                "tests_ts", f"{op_id}.test.ts", code, test_type="unit", framework="jest"
            )

    def generate_api_tests(
        self, ir: dict, payloads: List[Dict], base_url: str = "http://localhost:8000"
    ):
        """
        Generates integration tests for HTTP APIs using the new deterministic pipeline:

        1. Static Analyzer - Analyzes IR to detect resource requirements
        2. Setup Planner - Plans what resources need to be created
        3. Fixture Compiler - Generates actual fixture code (no LLM)
        4. Template Renderer - Renders tests with compiled fixtures
        5. LLM Polisher (optional) - Only cosmetic improvements
        """
        # Ensure base_url is a string and strip trailing slash for consistency
        base_url = str(base_url).rstrip("/")

        grouped = self._group_by_operation(payloads)

        # We need to look up path/method from the IR for each operation
        ops_map = {op["id"]: op for op in ir["operations"]}

        # === NEW PIPELINE ===

        # Step 1: Static Analysis - analyze all operations
        logger.debug("pipeline: running StaticTestAnalyzer")
        analyzer = StaticTestAnalyzer(ir, payloads)
        all_analyses = analyzer.analyze_all()

        # Step 2: Setup Planner - plan setup for each operation
        logger.debug("pipeline: initializing SetupPlanner")
        planner = SetupPlanner(payloads)

        # Step 3: Fixture Compiler - compile fixtures
        logger.debug("pipeline: initializing FixtureCompiler (base_url=%s)", base_url)
        fixture_compiler = FixtureCompiler(base_url)

        logger.debug(
            "pipeline: beginning per-operation rendering for %d operations",
            len(grouped),
        )
        for op_id, cases in grouped.items():
            op_details = ops_map.get(op_id)
            if not op_details:
                logger.debug("operation: %s not found in IR — skipping", op_id)
                continue

            # Get analysis and plan for this operation
            analysis = all_analyses.get(op_id)
            logger.debug("operation: %s analysis found=%s", op_id, bool(analysis))
            setup_plan = planner.plan(analysis, all_analyses) if analysis else None

            # Compile the fixture code
            if setup_plan and setup_plan.needs_setup:
                compiled_fixture = fixture_compiler.compile(setup_plan)
                placeholder_resolution = (
                    fixture_compiler.compile_placeholder_resolution()
                )
            else:
                compiled_fixture = fixture_compiler._compile_empty_fixture()
                placeholder_resolution = """    # No placeholder resolution needed for this operation
    if path_params is None:
        path_params = {}
    if not isinstance(path_params, dict):
        path_params = dict(path_params)"""

            # Extract error information
            errors = op_details.get("errors", [])
            error_codes = [e["status"] for e in errors]
            error_info = []
            for error in errors:
                error_data = {
                    "status": error["status"],
                    "description": error.get("description", "Error"),
                    "schema": error.get("schema"),
                }
                # Create a simplified schema summary for documentation
                if error.get("schema"):
                    error_data["schema_summary"] = self._summarize_schema(
                        error["schema"]
                    )
                error_info.append(error_data)

            # Extract path parameter names from operation inputs
            path_param_names = [
                p["name"] for p in op_details.get("inputs", {}).get("path", [])
            ]

            # Extract query parameter names
            query_param_names = [
                p["name"] for p in op_details.get("inputs", {}).get("query", [])
            ]

            # Extract body property names
            body_props = []
            body = op_details.get("inputs", {}).get("body", {})
            if body and body.get("schema"):
                body_props = list(body["schema"].get("properties", {}).keys())

            # Patch cases with USE_CREATED_RESOURCE for GET with path params
            method = op_details["method"].upper()
            has_path_params = bool(path_param_names)
            patched_cases = []
            for case in cases:
                patched_case = dict(case)
                if (
                    method in ("GET", "DELETE", "PUT", "PATCH")
                    and has_path_params
                    and case.get("intent", "").upper() == "HAPPY_PATH"
                ):
                    # Patch path_params to use a placeholder for created resource
                    patched_case["path_params"] = {
                        k: "USE_CREATED_RESOURCE" for k in path_param_names
                    }
                # Pre-format payloads and path_params for proper embedding
                patched_case["payload_formatted"] = _format_payload(
                    patched_case.get("payload", {})
                )
                patched_case["path_params_formatted"] = _format_payload(
                    patched_case.get("path_params", {})
                )
                patched_cases.append(patched_case)

            template = Template(API_TEST_TEMPLATE)
            code = template.render(
                base_url=base_url,
                path=op_details["path"],
                method=op_details["method"],
                operation_id=op_id,
                test_cases=patched_cases,
                error_codes=error_codes,
                error_info=error_info,
                path_param_names=path_param_names,
                query_param_names=query_param_names,
                body_props=body_props,
                compiled_fixture=compiled_fixture,
                placeholder_resolution=placeholder_resolution,
            )

            # Write file - LLM is now optional polisher only
            self._write_file("api", f"test_api_{op_id}.py", code, test_type="api")

    def generate_api_tests_jest(
        self, ir: dict, payloads: List[Dict], base_url: str = "http://localhost:8000"
    ):
        """
        Generates Jest-based integration tests for HTTP APIs.
        Uses the same deterministic pipeline as pytest:
        1. Static Analyzer - Analyzes IR to detect resource requirements
        2. Setup Planner - Plans what resources need to be created
        3. Fixture Compiler - Generates setup/teardown code (adapted for Jest)
        4. Template Renderer - Renders tests with compiled setup
        """
        # Ensure base_url is a string and strip trailing slash for consistency
        base_url = str(base_url).rstrip("/")

        grouped = self._group_by_operation(payloads)

        ops_map = {op["id"]: op for op in ir["operations"]}

        # === NEW PIPELINE (same as pytest) ===
        # Step 1: Static Analysis
        analyzer = StaticTestAnalyzer(ir, payloads)
        all_analyses = analyzer.analyze_all()

        # Step 2: Setup Planner
        planner = SetupPlanner(payloads)

        for op_id, cases in grouped.items():
            op_details = ops_map.get(op_id)
            if not op_details:
                continue

            # Get analysis and plan for this operation
            analysis = all_analyses.get(op_id)
            setup_plan = planner.plan(analysis, all_analyses) if analysis else None

            # Compile the setup code for Jest (beforeAll/afterAll)
            needs_setup = setup_plan and setup_plan.needs_setup
            jest_setup_code = ""
            jest_teardown_code = ""

            if needs_setup:
                jest_setup_code, jest_teardown_code = self._compile_jest_setup(
                    setup_plan, base_url
                )

            # Extract path parameter names
            path_param_names = [
                p["name"] for p in op_details.get("inputs", {}).get("path", [])
            ]

            # Patch cases with USE_CREATED_RESOURCE for GET/DELETE/PUT/PATCH
            method = op_details["method"].upper()
            has_path_params = bool(path_param_names)
            patched_cases = []
            for case in cases:
                patched_case = dict(case)
                if (
                    method in ("GET", "DELETE", "PUT", "PATCH")
                    and has_path_params
                    and case.get("intent", "").upper() == "HAPPY_PATH"
                ):
                    patched_case["path_params"] = {
                        k: "USE_CREATED_RESOURCE" for k in path_param_names
                    }
                patched_cases.append(patched_case)

            errors = op_details.get("errors", [])
            error_codes = [e["status"] for e in errors]
            error_info = []
            for error in errors:
                error_data = {
                    "status": error["status"],
                    "description": error.get("description", "Error"),
                    "schema": error.get("schema"),
                }
                if error.get("schema"):
                    error_data["schema_summary"] = self._summarize_schema(
                        error["schema"]
                    )
                error_info.append(error_data)

            template = Template(OPENAPI_JEST_TEST_TEMPLATE)
            code = template.render(
                base_url=base_url,
                path=op_details["path"],
                method=op_details["method"],
                operation_id=op_id,
                test_cases=patched_cases,
                error_codes=error_codes,
                error_info=error_info,
                needs_setup=needs_setup,
                jest_setup_code=jest_setup_code,
                jest_teardown_code=jest_teardown_code,
            )

            self._write_file(
                "api_jest",
                f"test_api_{op_id}.test.ts",
                code,
                test_type="api",
                framework="jest",
            )

        # Generate Jest configuration files for TypeScript support
        self._write_jest_config_files()

    def _compile_jest_setup(self, setup_plan, base_url: str) -> tuple:
        """
        Compile Jest beforeAll/afterAll code for resource creation.
        Returns (setup_code, teardown_code) as strings.
        """
        setup_lines = []
        teardown_lines = []

        for step in setup_plan.setup_steps:
            import json

            payload_str = json.dumps(step.payload)

            setup_lines.append(f"    // Create {step.resource_type} resource")
            setup_lines.append(
                f"    const createPayload_{step.resource_type} = {payload_str};"
            )
            setup_lines.append(
                f"    const createRes_{step.resource_type} = await fetch(`${{BASE_URL}}{step.endpoint}`, {{"
            )
            setup_lines.append(f"      method: 'POST',")
            setup_lines.append(
                f"      headers: {{ 'Content-Type': 'application/json' }},"
            )
            setup_lines.append(
                f"      body: JSON.stringify(createPayload_{step.resource_type}),"
            )
            setup_lines.append(f"    }});")
            setup_lines.append(f"    if (createRes_{step.resource_type}.ok) {{")
            setup_lines.append(
                f"      const data: any = await createRes_{step.resource_type}.json();"
            )
            setup_lines.append(
                f"      createdResources.push({{ type: '{step.resource_type}', id: data.id, endpoint: `${{BASE_URL}}{step.endpoint}/${{data.id}}` }});"
            )
            setup_lines.append(f"      placeholders['USE_CREATED_RESOURCE'] = data.id;")
            setup_lines.append(
                f"      placeholders['USE_CREATED_RESOURCE_{step.resource_type.upper()}'] = data.id;"
            )
            setup_lines.append(f"    }}")
            setup_lines.append("")

        teardown_lines.append(
            "    for (const resource of createdResources.reverse()) {"
        )
        teardown_lines.append("      try {")
        teardown_lines.append(
            "        await fetch(resource.endpoint, { method: 'DELETE' });"
        )
        teardown_lines.append("      } catch (e) {")
        teardown_lines.append(
            "        console.warn(`Cleanup failed for ${resource.type} ${resource.id}`);"
        )
        teardown_lines.append("      }")
        teardown_lines.append("    }")

        return "\n".join(setup_lines), "\n".join(teardown_lines)

    def _summarize_schema(self, schema: dict) -> str:
        """
        Create a brief summary of a schema for documentation purposes.
        """
        if not schema:
            return "N/A"

        schema_type = schema.get("type", "object")

        if schema_type == "object":
            props = schema.get("properties", {})
            if props:
                prop_names = list(props.keys())[:3]  # Show first 3 properties
                prop_str = ", ".join(prop_names)
                if len(props) > 3:
                    prop_str += ", ..."
                return f"object with properties: {prop_str}"
            return "object"
        elif schema_type == "array":
            items_type = schema.get("items", {}).get("type", "any")
            return f"array of {items_type}"
        else:
            return schema_type

    def _group_by_operation(self, payloads: List[Dict]) -> Dict[str, List[Dict]]:
        groups = defaultdict(list)
        for p in payloads:
            groups[p["operation_id"]].append(p)
        return groups

    def _extract_enum_types_from_ir(self, ir: dict) -> Dict[str, List[str]]:
        """
        Extract enum types used by each operation from the IR.

        Returns a dict mapping operation_id -> list of enum type names.
        Only includes types that are actually defined in the IR's types section.
        """
        # Build set of valid types from IR's types section
        valid_types = set()
        for type_def in ir.get("types", []):
            type_id = type_def.get("id")  # Parser uses "id" not "name"
            if type_id:
                valid_types.add(type_id)

        result = {}

        for op in ir.get("operations", []):
            op_id = op.get("id")
            if not op_id:
                continue

            enum_types = set()

            # Check body schema for enum types
            body = op.get("inputs", {}).get("body", {})
            if body:
                self._collect_enum_types(body.get("schema", {}), enum_types)

            # Check parameter schemas
            for param in op.get("inputs", {}).get("parameters", []):
                self._collect_enum_types(param.get("schema", {}), enum_types)

            # Filter to only valid types that exist in the source
            valid_enum_types = enum_types & valid_types
            if valid_enum_types:
                result[op_id] = sorted(valid_enum_types)

        return result

    def _extract_enum_conversions_from_ir(self, ir: dict) -> Dict[str, Dict[str, str]]:
        """
        Extract parameter-to-enum-type mappings from the IR.

        Returns a dict mapping operation_id -> {param_name: enum_type_name}
        Only includes types that are actually defined in the IR's types section.
        """
        # Build set of valid types from IR's types section
        valid_types = set()
        for type_def in ir.get("types", []):
            type_id = type_def.get("id")  # Parser uses "id" not "name"
            if type_id:
                valid_types.add(type_id)

        result = {}

        for op in ir.get("operations", []):
            op_id = op.get("id")
            if not op_id:
                continue

            conversions = {}

            # Check body schema properties for enum types
            body = op.get("inputs", {}).get("body", {})
            schema = body.get("schema", {})
            properties = schema.get("properties", {})

            for prop_name, prop_schema in properties.items():
                enum_type = prop_schema.get("x-enum-type")
                # Only add if this type actually exists in the source
                if enum_type and enum_type in valid_types:
                    conversions[prop_name] = enum_type

            if conversions:
                result[op_id] = conversions

        return result

    def _collect_enum_types(self, schema: dict, enum_types: set):
        """
        Recursively collect enum type names from a schema.
        """
        if not isinstance(schema, dict):
            return

        # Check for x-enum-type marker
        if "x-enum-type" in schema:
            enum_types.add(schema["x-enum-type"])

        # Recurse into properties
        for prop_schema in schema.get("properties", {}).values():
            self._collect_enum_types(prop_schema, enum_types)

        # Recurse into items
        if "items" in schema:
            self._collect_enum_types(schema["items"], enum_types)

        # Recurse into oneOf/anyOf
        for variant in schema.get("oneOf", []) + schema.get("anyOf", []):
            self._collect_enum_types(variant, enum_types)

    def _format_payload_with_enums(self, payload: dict, indent: int = 12) -> str:
        """
        Format a payload dict for embedding in test code, converting __ENUM__ markers
        to actual enum references.

        Args:
            payload: The payload dict to format
            indent: Indentation level for multiline formatting

        Returns:
            Formatted Python code string for the payload
        """
        import re

        # Use pprint to get a nice representation
        formatted = pprint.pformat(payload, width=80, indent=4)

        # Convert __ENUM__EnumType.MEMBER__ markers to actual enum references
        # Pattern matches: '__ENUM__EnumType.MEMBER__' or "__ENUM__EnumType.MEMBER__"
        def replace_enum(match):
            enum_ref = match.group(1)  # e.g., "Priority.HIGH"
            return enum_ref

        # Replace both single and double quoted versions
        formatted = re.sub(
            r"['\"]__ENUM__([A-Za-z_][A-Za-z0-9_.]+)__['\"]", replace_enum, formatted
        )

        # Add proper indentation for embedding in test code
        lines = formatted.split("\n")
        indented_lines = [lines[0]] + [" " * indent + line for line in lines[1:]]
        return "\n".join(indented_lines)

    def _write_jest_config_files(self):
        """
        Generate package.json and jest.config.js with TypeScript support for Jest tests.
        These files are written to the api_jest subdirectory.
        """
        import json

        jest_dir = os.path.join(self.output_dir, "api_jest")
        os.makedirs(jest_dir, exist_ok=True)

        # Generate package.json with ts-jest and TypeScript dependencies
        # Uses native fetch (Node.js 18+) so no node-fetch dependency needed
        package_json = {
            "name": "testsuitegen-api-tests",
            "version": "1.0.0",
            "description": "Auto-generated API tests by TestSuiteGen",
            "scripts": {
                "test": "jest --detectOpenHandles",
                "test:verbose": "jest --verbose --detectOpenHandles",
            },
            "devDependencies": {
                "@types/jest": "^29.5.14",
                "@types/node": "^22.10.5",
                "jest": "^29.7.0",
                "ts-jest": "^29.2.5",
                "typescript": "^5.7.2",
            },
        }

        package_json_path = os.path.join(jest_dir, "package.json")
        with open(package_json_path, "w", encoding="utf-8") as f:
            json.dump(package_json, f, indent=2)

        # Generate jest.config.js with ts-jest preset
        jest_config = """/** @type {import('ts-jest').JestConfigWithTsJest} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/*.test.ts'],
  moduleFileExtensions: ['ts', 'js', 'json'],
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  testTimeout: 30000,
  verbose: true,
};
"""
        jest_config_path = os.path.join(jest_dir, "jest.config.js")
        with open(jest_config_path, "w", encoding="utf-8") as f:
            f.write(jest_config)

        # Generate tsconfig.json for TypeScript configuration
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "lib": ["ES2020"],
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "declaration": False,
                "outDir": "./dist",
                "rootDir": ".",
            },
            "include": ["**/*.ts"],
            "exclude": ["node_modules", "dist"],
        }

        tsconfig_path = os.path.join(jest_dir, "tsconfig.json")
        with open(tsconfig_path, "w", encoding="utf-8") as f:
            json.dump(tsconfig, f, indent=2)

    def _write_file(
        self,
        subdir: str,
        filename: str,
        content: str,
        test_type: str = "api",
        framework: str = "pytest",
    ):
        dir_path = os.path.join(self.output_dir, subdir)
        os.makedirs(dir_path, exist_ok=True)
        filepath = os.path.join(dir_path, filename)

        content_to_write = content
        if self.llm_provider:
            try:
                if framework == "jest":
                    content_to_write = enhance_code_ts(
                        content,
                        provider=self.llm_provider,
                        model=self.llm_model,
                        test_type=test_type,
                    )
                else:
                    content_to_write = enhance_code_python(
                        content,
                        provider=self.llm_provider,
                        model=self.llm_model,
                        test_type=test_type,
                    )
            except Exception as e:
                # Rate limits or API failures: fall back to unenhanced code and disable LLM for subsequent files
                self.llm_provider = None

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content_to_write)

        # Format Python files with black after saving, only if syntax is valid
        if filename.endswith(".py"):
            try:
                import subprocess
                import py_compile

                try:
                    py_compile.compile(filepath, doraise=True)
                except py_compile.PyCompileError as ce:
                    pass
                else:
                    subprocess.run(["black", filepath], check=True)
            except Exception as e:
                pass

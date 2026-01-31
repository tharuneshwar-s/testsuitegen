import asyncio
import base64
import json
import logging
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from backend.src.config import (
    ARTIFACT_DIR,
    ENVIRONMENT,
    SUPABASE_URL,
    SUPABASE_KEY,
    SUPABASE_STORAGE_BUCKET,
)
from backend.src.core.intermediate_request import _build_ir
from backend.src.core.intents import _generate_intents
from backend.src.core.parsing import _parse_spec
from backend.src.core.payloads import _generate_payloads
from backend.src.database import store
from backend.src.exceptions import (
    IRBuildError,
    PayloadGenerationError,
    SpecDecodeError,
    SpecParsingError,
)
from backend.src.models.jobs import JobStatus
from backend.src.monitoring import log_capture

from testsuitegen.src.testsuite.generator import TestSuiteGenerator

_executor = ThreadPoolExecutor(max_workers=4)
logger = logging.getLogger(__name__)


def _generate_test_cases(
    job_id: str,
    ir: dict,
    payloads: list,
    source_type: str,
    base_url: str,
    llm_config: dict,
    framework: str = "pytest",
) -> dict:
    """Generate test cases from payloads using TestSuiteGenerator."""
    try:
        # Extract LLM config
        provider = llm_config.get("provider")
        model = llm_config.get("model")

        tests_dir = ARTIFACT_DIR / job_id / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("Storing test files in: %s", tests_dir)

        # Create test suite generator with artifact directory
        generator = TestSuiteGenerator(
            output_dir=str(tests_dir),
            llm_provider=provider,
            llm_model=model,
        )

        test_files = {}

        if source_type == "python":
            # Generate unit tests for Python functions
            module_name = ir.get("module_name", "test_module")
            generator.generate_python_unit_tests(ir, payloads, module_name)
        elif source_type == "typescript":
            # Generate Jest tests for TypeScript functions
            # The module path can be adjusted by the user in the generated files
            generator.generate_typescript_tests(ir, payloads)
        elif source_type == "openapi":
            # Generate API tests for OpenAPI using selected framework
            if framework.lower() == "jest":
                generator.generate_api_tests_jest(ir, payloads, base_url)
            else:
                generator.generate_api_tests(ir, payloads, base_url)
        else:
            # Fallback for other HTTP-like specs
            generator.generate_api_tests(ir, payloads, base_url)

        # Read generated test files from the artifact directory
        if tests_dir.exists():
            for file_path in tests_dir.rglob("*"):
                if file_path.suffix.lower() in {".py", ".ts", ".tsx", ".js"}:
                    logger.debug("Found test file: %s", file_path)
                    with open(file_path, "r", encoding="utf-8") as f:
                        test_files[file_path.name] = f.read()

            logger.info("Generated %d test files in %s", len(test_files), tests_dir)
        else:
            logger.warning("Tests directory does not exist: %s", tests_dir)

        return test_files
    except Exception as exc:
        logger.error("Failed to generate test cases: %s", exc)
        traceback.print_exc()
        return {}


def _extract_endpoints(ir: dict, source_type: str) -> list:
    """Extract API endpoints from the intermediate representation."""
    endpoints = []

    if source_type == "openapi":
        # Extract from OpenAPI IR
        operations = ir.get("operations", [])
        for op in operations:
            endpoint = {
                "method": op.get("method", "GET").upper(),
                "path": op.get("path", ""),
                "summary": op.get("summary", op.get("description", "")),
                "operation_id": op.get("operation_id", op.get("operationId", "")),
            }
            # Include inputs (path, query, headers, body parameters)
            if "inputs" in op:
                endpoint["inputs"] = op["inputs"]
            # Include outputs (responses)
            if "outputs" in op:
                endpoint["outputs"] = op["outputs"]
            endpoints.append(endpoint)
    else:
        # For Python/TypeScript, extract function signatures from operations
        functions = ir.get("operations", [])
        for func in functions:
            endpoint = {
                "method": "FUNC",
                "path": func.get("id", func.get("name", "")),
                "summary": func.get("description", func.get("docstring", "")),
                "operation_id": func.get("id", func.get("name", "")),
            }
            # Include inputs (function parameters)
            if "inputs" in func:
                endpoint["inputs"] = func["inputs"]
            # Include outputs (return type)
            if "outputs" in func:
                endpoint["outputs"] = func["outputs"]
            endpoints.append(endpoint)

        # Extract Types (Classes, Enums, Models)
        types = ir.get("types", [])
        for type_def in types:
            kind = type_def.get("kind", "model").upper()  # MODEL or ENUM
            endpoint = {
                "method": kind,  # MODEL or ENUM
                "path": type_def.get("id", ""),
                "summary": type_def.get("description", ""),
                "operation_id": type_def.get("id", ""),
            }

            # Map schema to inputs.body for visualization
            if kind == "MODEL":
                endpoint["inputs"] = {
                    "body": {
                        "content_type": "application/x-model",
                        "schema": type_def.get("schema", {}),
                    }
                }
            elif kind == "ENUM":
                # For Enum, we construct a schema that lists values
                values = type_def.get("values", [])
                endpoint["inputs"] = {
                    "body": {
                        "content_type": "application/x-enum",
                        "schema": {
                            "type": "string",
                            "enum": [v["name"] for v in values],
                            "x-enum-values": values,  # Custom field for frontend
                        },
                    }
                }

            endpoints.append(endpoint)

    return endpoints


def _run_pipeline(job_id, job_request, spec_json) -> dict:
    """Execute the test generation pipeline synchronously."""
    original_stdout = sys.stdout
    sys.stdout = log_capture.StreamCapture(job_id, original_stdout)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    local_logger = logging.getLogger(f"pipeline.{job_id}")
    local_logger.handlers = []
    local_logger.addHandler(handler)
    local_logger.setLevel(logging.INFO)

    try:
        source_type = job_request.get("source_type", "openapi")
        base_url = job_request.get("base_url", "http://localhost:8000")
        framework = job_request.get("framework", "pytest")

        # Step 1: Parsing Specification
        local_logger.info("Step 1: Parsing specification (source_type=%s)", source_type)
        asyncio.run(store.set_progress(job_id, 15))
        parsed_data = _parse_spec(spec_json, source_type=source_type)
        local_logger.info("Step 1 Completed: Specification parsed successfully")

        # Step 2: Building Intermediate Representation
        local_logger.info("Step 2: Building intermediate representation")
        asyncio.run(store.set_progress(job_id, 30))

        # Extract LLM config for IR enhancement
        llm_config = job_request.get("llm_config", {}) or {}
        # Use payload_enhancement config for IR enhancement as requested
        ir_llm_config = llm_config.get("payload_enhancement", {}) or {}
        provider = ir_llm_config.get("provider")
        model = ir_llm_config.get("model")

        ir = _build_ir(
            parsed_data=parsed_data,
            spec_json=spec_json,
            source_type=source_type,
            provider=provider,
            model=model,
        )
        local_logger.info("Step 2 Completed: Intermediate representation built")

        # Extract and save endpoints to Supabase
        endpoints = _extract_endpoints(ir, source_type)
        if endpoints:
            asyncio.run(store.save_endpoints(job_id, endpoints))
            local_logger.info("  Extracted %d API endpoints", len(endpoints))

        # Step 3: Generating Test Intents
        local_logger.info("Step 3: Generating test intents")
        asyncio.run(store.set_progress(job_id, 50))
        all_intents = _generate_intents(ir, job_request)
        local_logger.info(
            "Step 3 Completed: Generated %d test intents", len(all_intents)
        )

        # Step 4: Creating Payloads
        local_logger.info("Step 4: Creating Mock Data")
        asyncio.run(store.set_progress(job_id, 65))
        llm_config = job_request.get("llm_config", {}) or {}
        payload_llm_config = llm_config.get("payload_enhancement", {}) or {}
        final_payloads, enhanced_payloads = _generate_payloads(
            ir, all_intents, payload_llm_config
        )
        local_logger.info(
            "Step 4 Completed: Generated %d payloads", len(final_payloads)
        )

        # Step 5: Generating Test Cases
        local_logger.info("Step 5: Generating test cases")
        asyncio.run(store.set_progress(job_id, 80))
        test_llm_config = llm_config.get("test_enhancement", {}) or {}
        test_files = _generate_test_cases(
            job_id,
            ir,
            final_payloads,
            source_type,
            base_url,
            test_llm_config,
            framework,
        )
        local_logger.info("Step 5 Completed: Generated %d test files", len(test_files))

        # Step 6: Persisting Artifacts
        local_logger.info("Step 6: Persisting artifacts")
        asyncio.run(store.set_progress(job_id, 90))
        job_output_dir = ARTIFACT_DIR / job_id
        artifacts = _persist_artifacts(
            job_output_dir,
            ir,
            all_intents,
            final_payloads,
            enhanced_payloads,
            test_files,
        )
        local_logger.info(
            "Step 6 Completed: Artifacts persisted successfully (%d files)",
            len(artifacts),
        )
        asyncio.run(store.set_progress(job_id, 100))
        asyncio.run(store.mark_completed(job_id))

        local_logger.info("Pipeline completed successfully!")
        return {"success": True, "artifacts": artifacts}
    except (SpecParsingError, IRBuildError, PayloadGenerationError) as exc:
        local_logger.error("Pipeline failed: %s", exc)
        return {"success": False, "error": str(exc), "artifacts": []}
    except Exception as exc:  # noqa: B902
        local_logger.exception("Pipeline failed with unexpected error")
        raise
    finally:
        sys.stdout = original_stdout


def _persist_artifacts(
    job_output_dir: Path,
    ir: dict,
    intents: list,
    payloads: list,
    enhanced_payloads: list,
    test_files: dict = None,
):
    """Save artifacts to local filesystem and/or Supabase storage."""
    artifacts = []
    test_files = test_files or {}

    logger.info("Persisting artifacts - test_files count: %d", len(test_files))
    if test_files:
        logger.info("Test files to persist: %s", list(test_files.keys()))

    # In development, save to local filesystem
    if ENVIRONMENT == "development":
        job_output_dir.mkdir(parents=True, exist_ok=True)
        _save_json_artifact(job_output_dir, "1_ir", ir)
        _save_json_artifact(job_output_dir, "2_intents", intents)
        _save_json_artifact(job_output_dir, "3_payloads_final", payloads)
        _save_json_artifact(job_output_dir, "3_payloads_enhanced", enhanced_payloads)

        # Note: Test files are already saved in job_output_dir/tests by _generate_test_cases

        # Get local file paths
        local_artifacts = [
            str(file_path.relative_to(ARTIFACT_DIR))
            for file_path in job_output_dir.rglob("*")
            if file_path.is_file()
        ]
        logger.info("Saved %d artifacts to local filesystem", len(local_artifacts))

    # Upload to Supabase storage (both development and production)
    try:
        job_id = job_output_dir.name
        artifact_data = {
            "1_ir.json": ir,
            "2_intents.json": intents,
            "3_payloads_final.json": payloads,
            "3_payloads_enhanced.json": enhanced_payloads,
        }

        supabase_artifacts = _upload_to_supabase_storage(
            job_id, artifact_data, test_files
        )

        # In both development and production, return Supabase paths
        # In development, local files are also available for debugging
        artifacts = supabase_artifacts

        logger.info(
            "Artifacts persisted: %d files to %s",
            len(artifacts),
            "local & Supabase" if ENVIRONMENT == "development" else "Supabase only",
        )
    except Exception as exc:
        logger.warning("Failed to upload to Supabase storage: %s", exc)
        # In production, this is a critical failure
        if ENVIRONMENT == "production":
            raise
        # In development, fall back to local artifacts
        elif ENVIRONMENT == "development":
            artifacts = local_artifacts

    return artifacts


def _save_json_artifact(job_dir: Path, filename: str, payload):
    """Write JSON artifact to the job's artifact directory."""
    job_dir.mkdir(parents=True, exist_ok=True)
    outfile = job_dir / f"{filename}.json"
    with open(outfile, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    return outfile


def _upload_to_supabase_storage(
    job_id: str, artifacts: dict, test_files: dict = None
) -> list:
    """Upload artifacts to Supabase storage."""
    from supabase import create_client

    # Create client - use the base URL without modifications
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    uploaded_paths = []

    # Upload JSON artifacts
    for filename, payload in artifacts.items():
        # Convert payload to JSON bytes
        json_bytes = json.dumps(payload, indent=2).encode("utf-8")

        # Upload to Supabase storage
        storage_path = f"{job_id}/{filename}"
        try:
            supabase.storage.from_(SUPABASE_STORAGE_BUCKET).upload(
                path=storage_path,
                file=json_bytes,
                file_options={"content-type": "application/json", "upsert": "true"},
            )
            uploaded_paths.append(storage_path)
            logger.debug("Uploaded %s to Supabase storage", storage_path)
        except Exception as exc:
            logger.error("Failed to upload %s: %s", storage_path, exc)
            raise

    # Upload test files
    if test_files:
        logger.info("Uploading %d test files to Supabase storage", len(test_files))
        for filename, content in test_files.items():
            test_bytes = content.encode("utf-8")
            storage_path = f"{job_id}/tests/{filename}"
            try:
                supabase.storage.from_(SUPABASE_STORAGE_BUCKET).upload(
                    path=storage_path,
                    file=test_bytes,
                    file_options={"content-type": "text/plain", "upsert": "true"},
                )
                uploaded_paths.append(storage_path)
                logger.info("Uploaded test file: %s", storage_path)
            except Exception as exc:
                logger.error("Failed to upload test file %s: %s", storage_path, exc)
                raise
    else:
        logger.warning("No test files to upload to Supabase storage")

    return uploaded_paths


def _decode_spec(job_request: dict) -> str:
    """Decode base64 encoded spec data."""
    spec_base64 = job_request.get("spec_data")
    if not isinstance(spec_base64, str):
        raise SpecDecodeError("spec_data must be a base64-encoded string")
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=")
    cleaned = "".join(ch for ch in spec_base64.strip() if ch in allowed)
    if not cleaned:
        raise SpecDecodeError("spec_data is empty or invalid after cleaning")
    try:
        return base64.b64decode(cleaned, validate=True).decode("utf-8")
    except Exception as exc:  # noqa: B902
        raise SpecDecodeError(f"Invalid base64 spec_data: {exc}") from exc


async def execute_job(job_id: str, job_request: dict):
    """Execute a test generation job asynchronously."""
    try:
        # 1. Update Status: RUNNING
        await store.update_status(job_id, JobStatus.RUNNING)

        # 2. Decode Spec (fast, can run inline)
        spec_json = _decode_spec(job_request)

        # 3. Run blocking pipeline in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            _executor, _run_pipeline, job_id, job_request, spec_json
        )

        if not isinstance(result, dict):
            raise RuntimeError("Pipeline did not return a result dictionary")

        if result.get("success"):
            for artifact_path in result.get("artifacts", []):
                await store.add_artifact(job_id, artifact_path)
            # await store.set_progress(job_id, 100)
            await store.mark_completed(job_id)
        else:
            await store.mark_failed(job_id, result.get("error", "Unknown error"))

    except Exception as e:
        error_msg = f"{type(e).__name__}: {str(e)}"
        traceback.print_exc()
        await store.mark_failed(job_id, error_msg)

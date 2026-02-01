# OpenAPI Spec to Test Suite Generation

A comprehensive guide to how TestSuiteGen transforms OpenAPI specifications into complete, executable test suites.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Pipeline Stages](#pipeline-stages)
   - [Stage 1: OpenAPI Parsing](#stage-1-openapi-parsing)
   - [Stage 2: Intent Generation](#stage-2-intent-generation)
   - [Stage 3: Payload Generation](#stage-3-payload-generation)
   - [Stage 4: LLM Enhancement (Optional)](#stage-4-llm-enhancement-optional)
   - [Stage 5: Static Test Analysis](#stage-5-static-test-analysis)
   - [Stage 6: Setup Planning](#stage-6-setup-planning)
   - [Stage 7: Fixture Compilation](#stage-7-fixture-compilation)
   - [Stage 8: Test Suite Generation](#stage-8-test-suite-generation)
4. [Complete Example](#complete-example)
5. [Key Concepts](#key-concepts)

---

## Overview

TestSuiteGen is a deterministic, mutation-based test generation system that:

1. **Parses** OpenAPI specifications into an Intermediate Representation (IR)
2. **Generates** test intents covering functional, boundary, constraint, and security scenarios
3. **Produces** concrete test payloads by mutating a "Golden Record"
4. **Analyzes** resource dependencies between API operations
5. **Compiles** setup/teardown fixtures for stateful tests
6. **Outputs** ready-to-run Pytest test files

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  OpenAPI Spec   │────▶│    IR (JSON)    │────▶│   Test Intents  │
│   (YAML/JSON)   │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Test Suite     │◀────│ Compiled        │◀────│   Test Payloads │
│  (.py files)    │     │ Fixtures        │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Architecture

```
testsuitegen/src/
├── parsers/
│   └── openapi_parser/
│       └── parser.py          # Stage 1: OpenAPI → IR
├── generators/
│   ├── intent_generator/
│   │   └── openapi_intent/
│   │       └── generator.py   # Stage 2: IR → Intents
│   └── payloads_generator/
│       ├── generator.py       # Stage 3: Intents → Payloads
│       └── openapi_mutator/
│           └── mutator.py     # Mutation strategies
├── llm_enhancer/
│   └── payload_enhancer/
│       └── enhancer.py        # Stage 4: Payload enhancement
└── testsuite/
    ├── analyzer.py            # Stage 5: Static analysis
    ├── planner.py             # Stage 6: Setup planning
    ├── compiler.py            # Stage 7: Fixture compilation
    ├── generator.py           # Stage 8: Test generation
    └── templates.py           # Jinja2 templates
```

---

## Pipeline Stages

### Stage 1: OpenAPI Parsing

**File:** `parsers/openapi_parser/parser.py`

**Purpose:** Convert OpenAPI specification into a normalized Intermediate Representation (IR).

#### Input: OpenAPI Specification (YAML)

```yaml
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    post:
      operationId: createUser
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - email
                - name
              properties:
                email:
                  type: string
                  format: email
                  maxLength: 255
                name:
                  type: string
                  minLength: 1
                  maxLength: 100
                age:
                  type: integer
                  minimum: 0
                  maximum: 150
      responses:
        '201':
          description: User created
        '400':
          description: Validation error
        '422':
          description: Unprocessable entity

  /users/{user_id}:
    get:
      operationId: getUser
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      responses:
        '200':
          description: User found
        '404':
          description: User not found
```

#### Output: Intermediate Representation (IR)

```json
{
  "title": "User API",
  "version": "1.0.0",
  "operations": [
    {
      "id": "createUser",
      "kind": "http",
      "method": "POST",
      "path": "/users",
      "inputs": {
        "path": [],
        "query": [],
        "headers": [],
        "body": {
          "required": true,
          "schema": {
            "type": "object",
            "required": ["email", "name"],
            "properties": {
              "email": {
                "type": "string",
                "format": "email",
                "maxLength": 255,
                "nullable": false
              },
              "name": {
                "type": "string",
                "minLength": 1,
                "maxLength": 100,
                "nullable": false
              },
              "age": {
                "type": "integer",
                "minimum": 0,
                "maximum": 150,
                "nullable": false
              }
            },
            "nullable": false
          }
        }
      },
      "outputs": [
        {
          "status": 201,
          "description": "User created",
          "content_type": "application/json",
          "schema": null
        }
      ],
      "errors": [
        {
          "status": 400,
          "description": "Validation error",
          "content_type": null,
          "schema": null
        },
        {
          "status": 422,
          "description": "Unprocessable entity",
          "content_type": null,
          "schema": null
        }
      ]
    },
    {
      "id": "getUser",
      "kind": "http",
      "method": "GET",
      "path": "/users/{user_id}",
      "inputs": {
        "path": [
          {
            "name": "user_id",
            "required": true,
            "schema": {
              "type": "string",
              "format": "uuid",
              "nullable": false
            }
          }
        ],
        "query": [],
        "headers": [],
        "body": null
      },
      "outputs": [
        {
          "status": 200,
          "description": "User found",
          "content_type": null,
          "schema": null
        }
      ],
      "errors": [
        {
          "status": 404,
          "description": "User not found",
          "content_type": null,
          "schema": null
        }
      ]
    }
  ]
}
```

#### Key Transformations

| OpenAPI Feature | IR Transformation |
|-----------------|-------------------|
| `$ref` references | Fully resolved and inlined |
| `allOf` schemas | Merged into single schema |
| `parameters` | Grouped by location (path/query/header) |
| `requestBody` | Extracted to `inputs.body` |
| `responses` | Split into `outputs` (2xx) and `errors` (4xx) |

---

### Stage 2: Intent Generation

**File:** `generators/intent_generator/openapi_intent/generator.py`

**Purpose:** Analyze the IR schema and generate comprehensive test intents covering all testing scenarios.

#### Input: Single IR Operation

```json
{
  "id": "createUser",
  "kind": "http",
  "method": "POST",
  "path": "/users",
  "inputs": {
    "body": {
      "schema": {
        "type": "object",
        "required": ["email", "name"],
        "properties": {
          "email": { "type": "string", "format": "email", "maxLength": 255 },
          "name": { "type": "string", "minLength": 1, "maxLength": 100 },
          "age": { "type": "integer", "minimum": 0, "maximum": 150 }
        }
      }
    }
  },
  "errors": [{ "status": 422, "description": "Unprocessable entity" }]
}
```

#### Output: Test Intents

```json
[
  {
    "intent": "HAPPY_PATH",
    "target": "inputs.body",
    "field": null,
    "expected_status": "201",
    "description": "Valid request should succeed"
  },
  {
    "intent": "REQUIRED_FIELD_MISSING",
    "target": "inputs.body.email",
    "field": "email",
    "expected_status": "422",
    "description": "Missing required field: email"
  },
  {
    "intent": "REQUIRED_FIELD_MISSING",
    "target": "inputs.body.name",
    "field": "name",
    "expected_status": "422",
    "description": "Missing required field: name"
  },
  {
    "intent": "TYPE_VIOLATION",
    "target": "inputs.body.email",
    "field": "email",
    "expected_status": "422",
    "description": "Invalid type for field: email"
  },
  {
    "intent": "FORMAT_INVALID",
    "target": "inputs.body.email",
    "field": "email",
    "expected_status": "422",
    "description": "Invalid format for email field"
  },
  {
    "intent": "BOUNDARY_MAX_LENGTH_PLUS_ONE",
    "target": "inputs.body.email",
    "field": "email",
    "expected_status": "422",
    "description": "Exceeds maxLength constraint: 255 + 1"
  },
  {
    "intent": "BOUNDARY_MIN_LENGTH_MINUS_ONE",
    "target": "inputs.body.name",
    "field": "name",
    "expected_status": "422",
    "description": "Below minLength constraint: 1 - 1"
  },
  {
    "intent": "BOUNDARY_MIN_MINUS_ONE",
    "target": "inputs.body.age",
    "field": "age",
    "expected_status": "422",
    "description": "Below minimum constraint: 0 - 1"
  },
  {
    "intent": "BOUNDARY_MAX_PLUS_ONE",
    "target": "inputs.body.age",
    "field": "age",
    "expected_status": "422",
    "description": "Exceeds maximum constraint: 150 + 1"
  },
  {
    "intent": "SQL_INJECTION",
    "target": "inputs.body.name",
    "field": "name",
    "expected_status": "422",
    "description": "SQL injection attempt on name"
  },
  {
    "intent": "XSS_INJECTION",
    "target": "inputs.body.name",
    "field": "name",
    "expected_status": "422",
    "description": "XSS injection attempt on name"
  }
]
```

#### Intent Categories

| Category | Intent Types | Description |
|----------|--------------|-------------|
| **Functional** | `HAPPY_PATH`, `REQUIRED_FIELD_MISSING`, `NULLABLE_FIELD_NULL` | Core functionality tests |
| **Type** | `TYPE_VIOLATION`, `FORMAT_INVALID` | Data type validation |
| **Boundary** | `BOUNDARY_MIN_MINUS_ONE`, `BOUNDARY_MAX_PLUS_ONE`, `BOUNDARY_MIN_LENGTH_MINUS_ONE`, `BOUNDARY_MAX_LENGTH_PLUS_ONE` | Constraint boundary testing |
| **Enum** | `ENUM_INVALID`, `ENUM_VALID` | Enumeration validation |
| **Security** | `SQL_INJECTION`, `XSS_INJECTION`, `HEADER_INJECTION` | Security fuzzing |
| **Path** | `RESOURCE_NOT_FOUND`, `FORMAT_INVALID_PATH_PARAM` | Path parameter testing |

---

### Stage 3: Payload Generation

**File:** `generators/payloads_generator/generator.py`

**Purpose:** Transform intents into concrete test payloads using mutation-based generation.

#### Input: Intents + IR Schema

```json
{
  "intent": "REQUIRED_FIELD_MISSING",
  "target": "inputs.body.email",
  "field": "email",
  "expected_status": "422"
}
```

#### Process: Golden Record Mutation

1. **Build Golden Record** - Create a valid base payload from schema
2. **Apply Mutation** - Mutate based on intent type
3. **Return Payload** - Complete test case with metadata

```python
# Golden Record (valid payload)
{
    "email": "__PLACEHOLDER_STRING_email__",
    "name": "__PLACEHOLDER_STRING_name__",
    "age": 1
}

# After REQUIRED_FIELD_MISSING mutation for 'email'
{
    "name": "__PLACEHOLDER_STRING_name__",
    "age": 1
}
# email field is removed
```

#### Output: Test Payloads

```json
[
  {
    "operation_id": "createUser",
    "intent": "HAPPY_PATH",
    "target": "inputs.body",
    "field": null,
    "expected_status": "201",
    "payload": {
      "email": "__PLACEHOLDER_STRING_email__",
      "name": "__PLACEHOLDER_STRING_name__",
      "age": 1
    },
    "path_params": {},
    "headers": {}
  },
  {
    "operation_id": "createUser",
    "intent": "REQUIRED_FIELD_MISSING",
    "target": "inputs.body.email",
    "field": "email",
    "expected_status": "422",
    "payload": {
      "name": "__PLACEHOLDER_STRING_name__",
      "age": 1
    },
    "path_params": {},
    "headers": {}
  },
  {
    "operation_id": "createUser",
    "intent": "TYPE_VIOLATION",
    "target": "inputs.body.email",
    "field": "email",
    "expected_status": "422",
    "payload": {
      "email": "__INVALID_TYPE__",
      "name": "__PLACEHOLDER_STRING_name__",
      "age": 1
    },
    "path_params": {},
    "headers": {}
  },
  {
    "operation_id": "createUser",
    "intent": "BOUNDARY_MAX_LENGTH_PLUS_ONE",
    "target": "inputs.body.email",
    "field": "email",
    "expected_status": "422",
    "payload": {
      "email": "aaaaaaaaaa...(256 chars)...aaa",
      "name": "__PLACEHOLDER_STRING_name__",
      "age": 1
    },
    "path_params": {},
    "headers": {}
  },
  {
    "operation_id": "createUser",
    "intent": "SQL_INJECTION",
    "target": "inputs.body.name",
    "field": "name",
    "expected_status": "422",
    "payload": {
      "email": "__PLACEHOLDER_STRING_email__",
      "name": "' OR '1'='1",
      "age": 1
    },
    "path_params": {},
    "headers": {}
  }
]
```

#### Mutation Strategies

| Intent | Mutation Applied |
|--------|------------------|
| `REQUIRED_FIELD_MISSING` | Remove the field from payload |
| `TYPE_VIOLATION` | Replace with `__INVALID_TYPE__` marker |
| `NULLABLE_FIELD_NULL` | Set field to `null` |
| `BOUNDARY_MIN_MINUS_ONE` | Set to `minimum - 1` |
| `BOUNDARY_MAX_PLUS_ONE` | Set to `maximum + 1` |
| `BOUNDARY_MIN_LENGTH_MINUS_ONE` | Generate string with `minLength - 1` chars |
| `BOUNDARY_MAX_LENGTH_PLUS_ONE` | Generate string with `maxLength + 1` chars |
| `FORMAT_INVALID` | Generate invalid format value |
| `ENUM_INVALID` | Set to `__INVALID_ENUM_VALUE__` |
| `SQL_INJECTION` | Set to `' OR '1'='1` |
| `XSS_INJECTION` | Set to `<script>alert(1)</script>` |

---

### Stage 4: LLM Enhancement (Optional)

**File:** `llm_enhancer/payload_enhancer/enhancer.py`

**Purpose:** Replace placeholder values with realistic, context-aware test data.

#### Input: Payload with Placeholders

```json
{
  "email": "__PLACEHOLDER_STRING_email__",
  "name": "__PLACEHOLDER_STRING_name__",
  "age": 1
}
```

#### Output: Enhanced Payload

```json
{
  "email": "john.smith@example.com",
  "name": "John Smith",
  "age": 28
}
```

#### LLM Enhancement Rules

1. **Only HAPPY_PATH** - Only enhances valid test cases
2. **Structure Preserved** - Cannot add/remove/rename keys
3. **Type Preserved** - Cannot change data types
4. **Fallback** - Returns original payload on failure

#### Resilience Features

- **Circuit Breaker** - Stops LLM calls after 3 consecutive failures
- **Exponential Backoff** - Retries with delays (2s, 4s, 8s)
- **JSON Validation** - Strict validation of LLM responses

---

### Stage 5: Static Test Analysis

**File:** `testsuite/analyzer.py`

**Purpose:** Analyze which tests require prerequisite resources.

#### Input: IR Operations + Payloads

```json
{
  "operations": [
    { "id": "createUser", "method": "POST", "path": "/users" },
    { "id": "getUser", "method": "GET", "path": "/users/{user_id}" }
  ]
}
```

#### Analysis Rules

| Method | Path Pattern | Needs Setup? | Reason |
|--------|--------------|--------------|--------|
| POST | `/users` | ❌ No | Creates a new resource |
| GET | `/users/{id}` | ✅ Yes | Needs existing user |
| DELETE | `/users/{id}` | ✅ Yes | Needs existing user |
| PUT | `/users/{id}` | ✅ Yes | Needs existing user |
| GET | `/users/{user_id}/orders/{order_id}` | ✅ Yes | Needs user AND order |

#### Output: Test Analysis

```json
{
  "operation_id": "getUser",
  "method": "GET",
  "path": "/users/{user_id}",
  "needs_setup": true,
  "resource_requirements": [
    {
      "resource_type": "user",
      "endpoint": "/users",
      "param_name": "user_id",
      "id_field": "id",
      "schema": {
        "type": "object",
        "required": ["email", "name"],
        "properties": {
          "email": { "type": "string" },
          "name": { "type": "string" }
        }
      }
    }
  ],
  "create_operations": {
    "user": {
      "operation_id": "createUser",
      "path": "/users",
      "method": "POST"
    }
  }
}
```

---

### Stage 6: Setup Planning

**File:** `testsuite/planner.py`

**Purpose:** Create an executable plan for test data setup.

#### Input: Test Analysis

```json
{
  "operation_id": "getUser",
  "needs_setup": true,
  "resource_requirements": [
    {
      "resource_type": "user",
      "endpoint": "/users",
      "param_name": "user_id"
    }
  ]
}
```

#### Output: Setup Plan

```json
{
  "operation_id": "getUser",
  "needs_setup": true,
  "setup_steps": [
    {
      "step_id": 1,
      "action": "create",
      "resource_type": "user",
      "endpoint": "/users",
      "method": "POST",
      "payload": {
        "email": "testuser@example.com",
        "name": "Test User"
      },
      "variable_name": "created_user",
      "id_extraction": "response.json()['id']",
      "depends_on": []
    }
  ],
  "teardown_steps": [
    {
      "step_id": 1,
      "endpoint_template": "/users/{id}",
      "variable_name": "created_user_id"
    }
  ],
  "placeholder_mappings": {
    "user_id": "created_user_id"
  }
}
```

---

### Stage 7: Fixture Compilation

**File:** `testsuite/compiler.py`

**Purpose:** Convert setup plans into executable Python fixture code.

#### Input: Setup Plan

```json
{
  "operation_id": "getUser",
  "needs_setup": true,
  "setup_steps": [
    {
      "step_id": 1,
      "action": "create",
      "resource_type": "user",
      "endpoint": "/users",
      "method": "POST",
      "payload": { "email": "test@example.com", "name": "Test User" },
      "variable_name": "created_user"
    }
  ]
}
```

#### Output: Python Fixture Code

```python
@pytest.fixture(scope="module")
def test_data_setup(api_client):
    '''
    Setup fixture that creates prerequisite test resources.
    Auto-generated by TestSuiteGen - DO NOT EDIT MANUALLY.
    '''
    created_resources = []
    placeholders = {}

    # Create user resource
    created_user_payload = {
        "email": "test@example.com",
        "name": "Test User"
    }

    # Make unique to avoid conflicts on repeated runs
    import uuid as _uuid
    _unique_suffix = _uuid.uuid4().hex[:8]
    for _key in created_user_payload:
        if isinstance(created_user_payload[_key], str):
            if 'email' in _key.lower():
                parts = created_user_payload[_key].split('@')
                if len(parts) == 2:
                    created_user_payload[_key] = f"{parts[0]}_{_unique_suffix}@{parts[1]}"
            elif 'name' in _key.lower():
                created_user_payload[_key] = f"{created_user_payload[_key]}_{_unique_suffix}"

    created_user_response = api_client.post(
        f"{BASE_URL}/users",
        json=created_user_payload
    )
    
    if created_user_response.status_code in (200, 201):
        created_user_id = created_user_response.json().get('id')
        placeholders['user_id'] = created_user_id
        created_resources.append({
            'type': 'user',
            'id': created_user_id,
            'endpoint': f"/users/{created_user_id}"
        })
    else:
        print(f"Warning: Could not create user: {created_user_response.status_code}")

    yield {
        "created_resources": created_resources,
        "placeholders": placeholders,
    }

    # Teardown: Clean up created resources in reverse order
    for resource in reversed(created_resources):
        try:
            delete_response = api_client.delete(resource['endpoint'])
            if delete_response.status_code not in (200, 204, 404):
                print(f"Cleanup warning: {delete_response.status_code}")
        except Exception as e:
            print(f"Cleanup error: {e}")
```

---

### Stage 8: Test Suite Generation

**File:** `testsuite/generator.py`

**Purpose:** Render final test files using Jinja2 templates.

#### Input: All Components

- IR operations
- Test payloads
- Compiled fixtures
- Base URL configuration

#### Output: Complete Test File

```python
import pytest
import requests
import uuid
import re

BASE_URL = "http://localhost:8000"
ENDPOINT = "/users/{user_id}"
METHOD = "GET"

# Operation: getUser
# Error Codes Expected: 404
# Auto-generated by TestSuiteGen - Fixtures are pre-compiled


@pytest.fixture(scope="module")
def api_client():
    '''Provides a configured API client for testing.'''
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    yield session
    session.close()


@pytest.fixture(scope="module")
def test_data_setup(api_client):
    '''
    Setup fixture that creates prerequisite test resources.
    Auto-generated by TestSuiteGen - DO NOT EDIT MANUALLY.
    '''
    created_resources = []
    placeholders = {}

    # Create user resource
    created_user_payload = {"email": "test@example.com", "name": "Test User"}
    
    # ... (fixture code as shown above) ...

    yield {"created_resources": created_resources, "placeholders": placeholders}

    # Teardown
    for resource in reversed(created_resources):
        try:
            api_client.delete(resource['endpoint'])
        except Exception:
            pass


@pytest.mark.parametrize("intent, payload, path_params, expected_status", [
    pytest.param(
        "HAPPY_PATH",
        {},
        {"user_id": "USE_CREATED_RESOURCE"},
        200,
        id="HAPPY_PATH"
    ),
    pytest.param(
        "RESOURCE_NOT_FOUND",
        {},
        {"user_id": "550e8400-e29b-41d4-a716-446655440000"},
        404,
        id="RESOURCE_NOT_FOUND"
    ),
    pytest.param(
        "FORMAT_INVALID_PATH_PARAM",
        {},
        {"user_id": "not-a-valid-uuid"},
        422,
        id="FORMAT_INVALID_PATH_PARAM"
    ),
])
def test_getUser_contract(api_client, test_data_setup, intent, payload, path_params, expected_status):
    """
    Validates GET /users/{user_id} against the OpenAPI contract.
    Intent: {intent}
    Expected Status: {expected_status}
    """
    url = f"{BASE_URL}{ENDPOINT}"
    created_resources = test_data_setup.get("created_resources", [])

    # Resolve USE_CREATED_RESOURCE placeholders
    for param_name, param_value in path_params.items():
        if param_value == "USE_CREATED_RESOURCE":
            path_params[param_name] = test_data_setup.get("placeholders", {}).get(param_name)

    # Replace path parameters in URL
    for param_name in re.findall(r'\{(\w+)\}', url):
        param_value = path_params.get(param_name)
        if param_value:
            url = url.replace(f"{{{param_name}}}", str(param_value))

    # Make the request
    response = api_client.get(url, json=payload if payload else None)

    # Assert status code
    assert response.status_code == expected_status, (
        f"Expected {expected_status}, got {response.status_code}. "
        f"Response: {response.text}"
    )
```

---

## Complete Example

### End-to-End Flow

```
INPUT: petstore.yaml (OpenAPI Spec)
                │
                ▼
┌───────────────────────────────────────────┐
│ Stage 1: OpenAPI Parser                   │
│   - Resolves $ref                         │
│   - Normalizes schemas                    │
│   - Extracts operations                   │
└───────────────────────────────────────────┘
                │
                ▼ IR (JSON)
┌───────────────────────────────────────────┐
│ Stage 2: Intent Generator                 │
│   - HAPPY_PATH                            │
│   - REQUIRED_FIELD_MISSING (per field)    │
│   - BOUNDARY_* (per constraint)           │
│   - SQL_INJECTION, XSS_INJECTION          │
└───────────────────────────────────────────┘
                │
                ▼ Intents (List)
┌───────────────────────────────────────────┐
│ Stage 3: Payload Generator                │
│   - Builds Golden Record                  │
│   - Applies mutations per intent          │
│   - Returns test payloads                 │
└───────────────────────────────────────────┘
                │
                ▼ Payloads (List)
┌───────────────────────────────────────────┐
│ Stage 4: LLM Enhancement (Optional)       │
│   - Replaces placeholders                 │
│   - Adds realistic values                 │
│   - Validates structure preserved         │
└───────────────────────────────────────────┘
                │
                ▼ Enhanced Payloads
┌───────────────────────────────────────────┐
│ Stage 5: Static Test Analyzer             │
│   - Detects resource dependencies         │
│   - Maps POST → GET/DELETE relationships  │
│   - Identifies setup requirements         │
└───────────────────────────────────────────┘
                │
                ▼ Analysis Results
┌───────────────────────────────────────────┐
│ Stage 6: Setup Planner                    │
│   - Orders resource creation              │
│   - Plans teardown sequence               │
│   - Maps placeholders to variables        │
└───────────────────────────────────────────┘
                │
                ▼ Setup Plan
┌───────────────────────────────────────────┐
│ Stage 7: Fixture Compiler                 │
│   - Generates Python fixture code         │
│   - Adds uniqueness (UUID suffixes)       │
│   - Implements teardown cleanup           │
└───────────────────────────────────────────┘
                │
                ▼ Compiled Fixtures
┌───────────────────────────────────────────┐
│ Stage 8: Test Suite Generator             │
│   - Renders Jinja2 templates              │
│   - Combines fixtures + test cases        │
│   - Writes .py test files                 │
└───────────────────────────────────────────┘
                │
                ▼
OUTPUT: test_createUser.py, test_getUser.py, ...
```

---

## Key Concepts

### Golden Record Pattern

Every test payload starts from a known-valid base payload (the "Golden Record"):

```python
# Golden Record for createUser
{
    "email": "valid@example.com",
    "name": "Valid Name",
    "age": 25
}

# Mutation for REQUIRED_FIELD_MISSING on 'email'
{
    "name": "Valid Name",  # Kept from Golden Record
    "age": 25              # Kept from Golden Record
}
# Only 'email' is removed - everything else stays valid
```

### Placeholder System

Placeholders allow deterministic generation with optional LLM enhancement:

| Placeholder | Meaning | LLM Replacement Example |
|-------------|---------|-------------------------|
| `__PLACEHOLDER_STRING_email__` | String field named email | `john.doe@company.com` |
| `__PLACEHOLDER_STRING_name__` | String field named name | `John Doe` |
| `__INVALID_TYPE__` | Type violation marker | Kept as-is (test data) |
| `USE_CREATED_RESOURCE` | Use fixture-created ID | Resolved at runtime |

### Resource Dependency Resolution

The analyzer automatically detects dependencies:

```
POST /users          → Creates 'user' resource
GET /users/{id}      → Needs 'user' → Setup creates user first
DELETE /users/{id}   → Needs 'user' → Setup creates user first

POST /users/{user_id}/orders    → Needs 'user' → Setup creates user first
GET /orders/{order_id}          → Needs 'order' → Setup creates order first
```

### Test Categories Generated

| Category | Intent Examples | Expected Outcome |
|----------|-----------------|------------------|
| **Happy Path** | `HAPPY_PATH` | 2xx Success |
| **Required Fields** | `REQUIRED_FIELD_MISSING` | 422 Validation Error |
| **Type Validation** | `TYPE_VIOLATION` | 422 Invalid Type |
| **Boundary Testing** | `BOUNDARY_MAX_PLUS_ONE` | 422 Constraint Violation |
| **Security** | `SQL_INJECTION`, `XSS_INJECTION` | 422 or Sanitized |
| **Resource** | `RESOURCE_NOT_FOUND` | 404 Not Found |

---

## Summary

TestSuiteGen provides a **deterministic, comprehensive** approach to API test generation:

1. **No Manual Test Writing** - Tests are derived from the OpenAPI spec
2. **Complete Coverage** - Functional, boundary, and security tests
3. **Stateful Support** - Automatic fixture generation for dependent resources
4. **LLM Optional** - Works without LLM; uses it only for realistic data
5. **Ready to Run** - Generated tests work immediately with pytest

```bash
# Generate tests
python -m testsuitegen generate --spec petstore.yaml --output tests/

# Run tests
pytest tests/ -v
```

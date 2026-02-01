# Python Function to Pytest Test Suite

A comprehensive guide to how TestSuiteGen transforms Python function definitions into Pytest test suites.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Pipeline Stages](#pipeline-stages)
   - [Stage 1: Python AST Parsing](#stage-1-python-ast-parsing)
   - [Stage 2: Intent Generation](#stage-2-intent-generation)
   - [Stage 3: Payload Generation](#stage-3-payload-generation)
   - [Stage 4: LLM Enhancement (Optional)](#stage-4-llm-enhancement-optional)
   - [Stage 5: Pytest Generation](#stage-5-pytest-generation)
4. [Complete Example](#complete-example)
5. [Supported Python Features](#supported-python-features)

---

## Overview

TestSuiteGen parses Python source code using the `ast` module to extract function signatures and type hints, then generates comprehensive Pytest test suites.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Python Source  │────▶│    IR (JSON)    │────▶│   Test Intents  │
│   (.py file)    │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Pytest File    │◀────│  Template       │◀────│   Test Payloads │
│  (test_*.py)    │     │  Rendering      │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Architecture

```
testsuitegen/src/
├── parsers/
│   └── python_parser/
│       └── parser.py              # Stage 1: Python → IR
├── generators/
│   ├── intent_generator/
│   │   └── python_intent/
│   │       └── generator.py       # Stage 2: IR → Intents
│   └── payloads_generator/
│       ├── generator.py           # Stage 3: Intents → Payloads
│       └── python_mutator/
│           └── mutator.py         # Python-specific mutations
├── llm_enhancer/
│   └── python_enhancer/
│       └── test_suite_enhancer/
│           └── enhancer.py        # Stage 4: Optional enhancement
└── testsuite/
    ├── generator.py               # Stage 5: Test generation
    └── templates.py               # UNIT_TEST_TEMPLATE
```

---

## Pipeline Stages

### Stage 1: Python AST Parsing

**File:** `parsers/python_parser/parser.py`

**Purpose:** Convert Python source code into an Intermediate Representation (IR) using Python's built-in `ast` module.

#### Input: Python Source Code

```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"


@dataclass
class User:
    """User data model."""
    name: str
    email: str
    age: int
    status: Status


def create_user(
    name: str,
    email: str,
    age: int,
    status: Status = Status.PENDING,
    tags: Optional[List[str]] = None
) -> User:
    """
    Creates a new user with validation.
    
    Args:
        name: User's full name (1-100 chars)
        email: Valid email address
        age: User's age (0-150)
        status: Account status
        tags: Optional list of tags
        
    Returns:
        User object
        
    Raises:
        ValueError: If validation fails
    """
    if not name or len(name) > 100:
        raise ValueError("Name must be 1-100 characters")
    if age < 0 or age > 150:
        raise ValueError("Age must be between 0 and 150")
    if "@" not in email:
        raise ValueError("Invalid email format")
    
    return User(name=name, email=email, age=age, status=status)
```

#### Parsing Process

1. **Parse AST** - `ast.parse(source_code)`
2. **First Pass** - Extract all classes (Enums, Dataclasses, Models)
3. **Second Pass** - Extract all function definitions
4. **Type Resolution** - Convert type hints to JSON Schema

#### Output: Intermediate Representation (IR)

```json
{
  "operations": [
    {
      "id": "create_user",
      "kind": "function",
      "async": false,
      "description": "Creates a new user with validation.\n\nArgs:\n    name: User's full name...",
      "metadata": {
        "decorators": []
      },
      "inputs": {
        "path": [],
        "query": [],
        "headers": [],
        "body": {
          "content_type": "application/json",
          "required": true,
          "schema": {
            "type": "object",
            "properties": {
              "name": {
                "type": "string"
              },
              "email": {
                "type": "string"
              },
              "age": {
                "type": "integer"
              },
              "status": {
                "type": "string",
                "enum": ["active", "inactive", "pending"],
                "x-enum-type": "Status"
              },
              "tags": {
                "type": "array",
                "items": { "type": "string" },
                "nullable": true
              }
            },
            "required": ["name", "email", "age"],
            "additionalProperties": false
          }
        }
      },
      "outputs": [
        {
          "status": 200,
          "content_type": "application/json",
          "schema": {
            "type": "object",
            "x-custom-type": "User"
          }
        }
      ],
      "errors": []
    }
  ],
  "types": [
    {
      "id": "Status",
      "kind": "enum",
      "description": "",
      "values": [
        { "name": "ACTIVE", "value": "active" },
        { "name": "INACTIVE", "value": "inactive" },
        { "name": "PENDING", "value": "pending" }
      ]
    },
    {
      "id": "User",
      "kind": "model",
      "description": "User data model.",
      "metadata": {
        "decorators": ["@dataclass"],
        "is_dataclass": true
      },
      "schema": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string" },
          "age": { "type": "integer" },
          "status": { "x-enum-type": "Status" }
        },
        "required": ["name", "email", "age", "status"]
      }
    }
  ]
}
```

#### Type Mapping

| Python Type | JSON Schema |
|-------------|-------------|
| `str` | `{"type": "string"}` |
| `int` | `{"type": "integer"}` |
| `float` | `{"type": "number"}` |
| `bool` | `{"type": "boolean"}` |
| `List[T]` | `{"type": "array", "items": {...}}` |
| `Dict[K, V]` | `{"type": "object", "additionalProperties": {...}}` |
| `Optional[T]` | `{..., "nullable": true}` |
| `Union[A, B]` | `{"oneOf": [{...}, {...}]}` |
| `Literal["a", "b"]` | `{"enum": ["a", "b"]}` |
| `Enum` subclass | `{"type": "string", "enum": [...], "x-enum-type": "..."}` |
| Custom class | `{"type": "object", "x-custom-type": "..."}` |

---

### Stage 2: Intent Generation

**File:** `generators/intent_generator/python_intent/generator.py`

**Purpose:** Analyze the IR schema and generate test intents specific to Python functions.

#### Input: Single IR Operation

```json
{
  "id": "create_user",
  "kind": "function",
  "inputs": {
    "body": {
      "schema": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string" },
          "age": { "type": "integer" },
          "status": { "type": "string", "enum": ["active", "inactive", "pending"] },
          "tags": { "type": "array", "nullable": true }
        },
        "required": ["name", "email", "age"]
      }
    }
  }
}
```

#### Output: Test Intents

```json
[
  {
    "intent": "HAPPY_PATH",
    "target": "body",
    "field": null,
    "expected": "200",
    "description": "Valid call with all correct arguments"
  },
  {
    "intent": "REQUIRED_ARG_MISSING",
    "target": "body.name",
    "field": "name",
    "expected": "400",
    "description": "Missing required argument: name"
  },
  {
    "intent": "REQUIRED_ARG_MISSING",
    "target": "body.email",
    "field": "email",
    "expected": "400",
    "description": "Missing required argument: email"
  },
  {
    "intent": "REQUIRED_ARG_MISSING",
    "target": "body.age",
    "field": "age",
    "expected": "400",
    "description": "Missing required argument: age"
  },
  {
    "intent": "TYPE_VIOLATION",
    "target": "body.name",
    "field": "name",
    "expected": "400",
    "description": "Wrong type for argument: name"
  },
  {
    "intent": "TYPE_VIOLATION",
    "target": "body.age",
    "field": "age",
    "expected": "400",
    "description": "Wrong type for argument: age"
  },
  {
    "intent": "NULL_NOT_ALLOWED",
    "target": "body.name",
    "field": "name",
    "expected": "400",
    "description": "None passed to non-nullable argument: name"
  },
  {
    "intent": "ENUM_MISMATCH",
    "target": "body.status",
    "field": "status",
    "expected": "400",
    "description": "Invalid enum value for: status"
  },
  {
    "intent": "UNEXPECTED_ARGUMENT",
    "target": "body",
    "field": null,
    "expected": "400",
    "description": "Unexpected keyword argument passed"
  },
  {
    "intent": "SQL_INJECTION",
    "target": "body.name",
    "field": "name",
    "expected": "400",
    "description": "SQL injection attempt on: name"
  },
  {
    "intent": "XSS_INJECTION",
    "target": "body.email",
    "field": "email",
    "expected": "400",
    "description": "XSS injection attempt on: email"
  }
]
```

#### Python-Specific Intent Categories

| Category | Intent Types | Description |
|----------|--------------|-------------|
| **Functional** | `HAPPY_PATH` | Valid function call |
| **Structural** | `REQUIRED_ARG_MISSING`, `UNEXPECTED_ARGUMENT`, `TOO_MANY_POS_ARGS` | Argument structure validation |
| **Type** | `TYPE_VIOLATION`, `NULL_NOT_ALLOWED`, `ARRAY_ITEM_TYPE_VIOLATION` | Type hint validation |
| **Constraint** | `BOUNDARY_MIN_MINUS_ONE`, `BOUNDARY_MAX_PLUS_ONE`, `STRING_TOO_SHORT`, `STRING_TOO_LONG` | Value constraints |
| **Enum** | `ENUM_MISMATCH` | Enum value validation |
| **Security** | `SQL_INJECTION`, `XSS_INJECTION` | Security fuzzing (if function has validation) |

---

### Stage 3: Payload Generation

**File:** `generators/payloads_generator/python_mutator/mutator.py`

**Purpose:** Transform intents into concrete test payloads (function arguments).

#### Input: Intent + Schema

```json
{
  "intent": "REQUIRED_ARG_MISSING",
  "target": "body.name",
  "field": "name",
  "expected": "400"
}
```

#### Process: Golden Record Mutation

1. **Build Golden Record** - Create valid arguments from schema
2. **Apply Mutation** - Remove/modify based on intent
3. **Return Payload** - Complete test case

```python
# Golden Record (valid arguments)
{
    "name": "__PLACEHOLDER_STRING_name__",
    "email": "__PLACEHOLDER_STRING_email__",
    "age": 1,
    "status": "active"
}

# After REQUIRED_ARG_MISSING mutation for 'name'
{
    "email": "__PLACEHOLDER_STRING_email__",
    "age": 1,
    "status": "active"
}
# 'name' argument is removed
```

#### Output: Test Payloads

```json
[
  {
    "operation_id": "create_user",
    "intent": "HAPPY_PATH",
    "expected_status": 200,
    "payload": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 25,
      "status": "active"
    }
  },
  {
    "operation_id": "create_user",
    "intent": "REQUIRED_ARG_MISSING",
    "field": "name",
    "expected_status": 400,
    "payload": {
      "email": "john@example.com",
      "age": 25,
      "status": "active"
    }
  },
  {
    "operation_id": "create_user",
    "intent": "TYPE_VIOLATION",
    "field": "age",
    "expected_status": 400,
    "payload": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": "__INVALID_TYPE__",
      "status": "active"
    }
  },
  {
    "operation_id": "create_user",
    "intent": "ENUM_MISMATCH",
    "field": "status",
    "expected_status": 400,
    "payload": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 25,
      "status": "__INVALID_ENUM_VALUE__"
    }
  },
  {
    "operation_id": "create_user",
    "intent": "UNEXPECTED_ARGUMENT",
    "expected_status": 400,
    "payload": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 25,
      "status": "active",
      "__unexpected_kwarg__": "unexpected_value"
    }
  },
  {
    "operation_id": "create_user",
    "intent": "SQL_INJECTION",
    "field": "name",
    "expected_status": 400,
    "payload": {
      "name": "' OR '1'='1",
      "email": "john@example.com",
      "age": 25,
      "status": "active"
    }
  }
]
```

#### Python Mutation Strategies

| Intent | Mutation Applied |
|--------|------------------|
| `REQUIRED_ARG_MISSING` | Remove the argument from kwargs |
| `UNEXPECTED_ARGUMENT` | Add `__unexpected_kwarg__` key |
| `TYPE_VIOLATION` | Set to `__INVALID_TYPE__` marker |
| `NULL_NOT_ALLOWED` | Set to `None` |
| `ENUM_MISMATCH` | Set to `__INVALID_ENUM_VALUE__` |
| `ARRAY_ITEM_TYPE_VIOLATION` | Set array with wrong item type |
| `SQL_INJECTION` | Set to `' OR '1'='1` |
| `XSS_INJECTION` | Set to `<script>alert(1)</script>` |

---

### Stage 4: LLM Enhancement (Optional)

**File:** `llm_enhancer/python_enhancer/test_suite_enhancer/enhancer.py`

**Purpose:** Replace placeholder values with realistic test data.

#### Input: Payload with Placeholders

```python
{
    "name": "__PLACEHOLDER_STRING_name__",
    "email": "__PLACEHOLDER_STRING_email__",
    "age": 1
}
```

#### Output: Enhanced Payload

```python
{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "age": 28
}
```

---

### Stage 5: Pytest Generation

**File:** `testsuite/generator.py` + `templates.py`

**Purpose:** Render final Pytest test files using Jinja2 templates.

#### Input: All Components

- IR operation
- Test payloads
- Enum types for imports
- Module path

#### Output: Complete Pytest File

```python
import pytest
from user_module import create_user, Status

# Auto-generated by TestSuiteGen
# Operation: create_user

# Enum mapping for automatic conversion
_ENUM_MAP = {
    "Status": Status,
}


class TestCreateUser:

    @pytest.mark.parametrize("intent, kwargs, expected_status", [
        pytest.param(
            "HAPPY_PATH",
            {'name': 'John Doe', 'email': 'john@example.com', 'age': 25, 'status': 'active'},
            200,
            id="HAPPY_PATH"
        ),
        pytest.param(
            "REQUIRED_ARG_MISSING",
            {'email': 'john@example.com', 'age': 25, 'status': 'active'},
            400,
            id="REQUIRED_ARG_MISSING"
        ),
        pytest.param(
            "TYPE_VIOLATION",
            {'name': 'John Doe', 'email': 'john@example.com', 'age': '__INVALID_TYPE__', 'status': 'active'},
            400,
            id="TYPE_VIOLATION"
        ),
        pytest.param(
            "ENUM_MISMATCH",
            {'name': 'John Doe', 'email': 'john@example.com', 'age': 25, 'status': '__INVALID_ENUM_VALUE__'},
            400,
            id="ENUM_MISMATCH"
        ),
        pytest.param(
            "UNEXPECTED_ARGUMENT",
            {'name': 'John Doe', 'email': 'john@example.com', 'age': 25, 'status': 'active', '__unexpected_kwarg__': 'value'},
            400,
            id="UNEXPECTED_ARGUMENT"
        ),
        pytest.param(
            "SQL_INJECTION",
            {'name': "' OR '1'='1", 'email': 'john@example.com', 'age': 25, 'status': 'active'},
            400,
            id="SQL_INJECTION"
        ),
    ])
    def test_create_user_contract(self, intent, kwargs, expected_status):
        """
        Contract testing for create_user.
        Intent: {intent}
        Expected: {expected_status} (400/422 = Exception)
        """
        
        # Convert enum string values to actual enum instances for HAPPY_PATH
        if expected_status < 400:
            if "status" in kwargs and isinstance(kwargs["status"], str):
                try:
                    kwargs["status"] = Status(kwargs["status"].lower())
                except ValueError:
                    pass  # Let the test fail with invalid enum value
        
        # Negative Tests (Expect Exceptions)
        if expected_status >= 400:
            # We expect TypeError for structural issues, ValueError for constraints
            with pytest.raises((ValueError, TypeError, AssertionError, AttributeError)):
                create_user(**kwargs)
        
        # Happy Path (Expect Return Value)
        else:
            result = create_user(**kwargs)
            assert result is not None
```

---

## Complete Example

### End-to-End Flow

```
INPUT: user_module.py (Python Source)
                │
                ▼
┌───────────────────────────────────────────┐
│ Stage 1: Python AST Parser                │
│   - ast.parse(source_code)                │
│   - Extract classes (Enums, Dataclasses)  │
│   - Extract functions with type hints     │
│   - Build type registry                   │
└───────────────────────────────────────────┘
                │
                ▼ IR (JSON)
┌───────────────────────────────────────────┐
│ Stage 2: Python Intent Generator          │
│   - HAPPY_PATH                            │
│   - REQUIRED_ARG_MISSING (per required)   │
│   - TYPE_VIOLATION (per argument)         │
│   - ENUM_MISMATCH (for enum params)       │
│   - Security tests (if validation found)  │
└───────────────────────────────────────────┘
                │
                ▼ Intents (List)
┌───────────────────────────────────────────┐
│ Stage 3: Python Payload Generator         │
│   - Uses PythonMutator                    │
│   - Builds Golden Record                  │
│   - Applies mutations per intent          │
└───────────────────────────────────────────┘
                │
                ▼ Payloads (List)
┌───────────────────────────────────────────┐
│ Stage 4: LLM Enhancement (Optional)       │
│   - Replaces placeholders                 │
│   - Adds realistic values                 │
└───────────────────────────────────────────┘
                │
                ▼ Enhanced Payloads
┌───────────────────────────────────────────┐
│ Stage 5: Pytest Generator                 │
│   - UNIT_TEST_TEMPLATE                    │
│   - @pytest.mark.parametrize              │
│   - Enum import/conversion                │
│   - pytest.raises for negative tests      │
└───────────────────────────────────────────┘
                │
                ▼
OUTPUT: test_create_user.py
```

---

## Supported Python Features

### Type Hints

| Feature | Example | Supported |
|---------|---------|-----------|
| Basic types | `str`, `int`, `float`, `bool` | ✅ |
| List | `List[str]`, `list[int]` | ✅ |
| Dict | `Dict[str, int]`, `dict[str, Any]` | ✅ |
| Tuple | `Tuple[int, str]` | ✅ |
| Set | `Set[str]`, `FrozenSet[int]` | ✅ |
| Optional | `Optional[str]` | ✅ |
| Union | `Union[str, int]` | ✅ |
| Literal | `Literal["a", "b", "c"]` | ✅ |
| Custom classes | `User`, `Order` | ✅ |
| Generics | `T`, `Generic[T]` | Partial |
| Callable | `Callable[[int], str]` | ❌ |
| `*args`, `**kwargs` | | ❌ |

### Classes

| Feature | Example | Supported |
|---------|---------|-----------|
| Enum | `class Status(Enum)` | ✅ |
| Dataclass | `@dataclass class User` | ✅ |
| Pydantic BaseModel | `class User(BaseModel)` | ✅ |
| TypedDict | `class UserDict(TypedDict)` | ✅ |
| NamedTuple | `class Point(NamedTuple)` | ✅ |

### Functions

| Feature | Example | Supported |
|---------|---------|-----------|
| Regular functions | `def func(x: int)` | ✅ |
| Async functions | `async def func(x: int)` | ✅ |
| Default values | `def func(x: int = 10)` | ✅ |
| Decorators | `@decorator` | ✅ (recorded) |
| Docstrings | `"""Docstring"""` | ✅ |
| Return type | `-> User` | ✅ |

---

## Running Generated Tests

```bash
# Run all generated tests
pytest generated_tests/unit/ -v

# Run specific test
pytest generated_tests/unit/test_create_user.py -v

# Run with coverage
pytest generated_tests/unit/ --cov=user_module
```

---

## Summary

The Python Function to Pytest pipeline produces:

1. **Type-Aware Tests** - Leverages Python type hints for comprehensive testing
2. **Enum Support** - Automatic enum conversion for happy path tests
3. **Exception Testing** - Uses `pytest.raises` for negative test cases
4. **Parameterized Tests** - `@pytest.mark.parametrize` for data-driven testing
5. **No HTTP** - Direct function calls, no server needed
6. **Ready to Run** - Works immediately with `pytest`

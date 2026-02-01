# OpenAPI Spec to Jest Test Suite (TypeScript)

A comprehensive guide to how TestSuiteGen transforms OpenAPI specifications into Jest/TypeScript test suites.

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
   - [Stage 6: Setup/Teardown Generation](#stage-6-setupteardown-generation)
   - [Stage 7: Jest Test Rendering](#stage-7-jest-test-rendering)
4. [Complete Example](#complete-example)
5. [Jest-Specific Features](#jest-specific-features)

---

## Overview

TestSuiteGen generates Jest test suites for API testing using native `fetch` (Node.js 18+). The generated tests:

1. **Use TypeScript** - Full type safety with TypeScript annotations
2. **Native fetch** - No axios dependency, uses built-in fetch API
3. **Parameterized Tests** - Uses Jest's `it.each()` for data-driven testing
4. **Automatic Setup/Teardown** - Manages prerequisite resources via `beforeAll`/`afterAll`

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  OpenAPI Spec   │────▶│    IR (JSON)    │────▶│   Test Intents  │
│   (YAML/JSON)   │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Jest Test      │◀────│ Setup/Teardown  │◀────│   Test Payloads │
│  (.test.ts)     │     │ beforeAll/After │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Architecture

```
testsuitegen/src/
├── parsers/
│   └── openapi_parser/
│       └── parser.py           # Stage 1: OpenAPI → IR
├── generators/
│   ├── intent_generator/
│   │   └── openapi_intent/
│   │       └── generator.py    # Stage 2: IR → Intents
│   └── payloads_generator/
│       ├── generator.py        # Stage 3: Intents → Payloads
│       └── openapi_mutator/
│           └── mutator.py      # Mutation strategies
├── llm_enhancer/
│   └── payload_enhancer/       # Stage 4: Optional LLM enhancement
│   └── typescript_enhancer/
│       └── test_suite_enhancer/
│           └── enhancer.py     # Jest code polishing
└── testsuite/
    ├── analyzer.py             # Stage 5: Static analysis
    ├── generator.py            # Stage 6-7: Test generation
    └── templates.py            # OPENAPI_JEST_TEST_TEMPLATE
```

---

## Pipeline Stages

### Stage 1: OpenAPI Parsing

**File:** `parsers/openapi_parser/parser.py`

**Purpose:** Convert OpenAPI specification into a normalized Intermediate Representation (IR).

*(Same as Pytest pipeline - see OPENAPI_TO_TESTSUITE.md)*

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
              required: [email, name]
              properties:
                email:
                  type: string
                  format: email
                name:
                  type: string
      responses:
        '201':
          description: User created
        '422':
          description: Validation error

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
          description: Not found
```

#### Output: IR (JSON)

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
        "body": {
          "schema": {
            "type": "object",
            "required": ["email", "name"],
            "properties": {
              "email": { "type": "string", "format": "email" },
              "name": { "type": "string" }
            }
          }
        }
      },
      "outputs": [{ "status": 201 }],
      "errors": [{ "status": 422 }]
    },
    {
      "id": "getUser",
      "kind": "http",
      "method": "GET",
      "path": "/users/{user_id}",
      "inputs": {
        "path": [{ "name": "user_id", "schema": { "type": "string", "format": "uuid" }}]
      },
      "outputs": [{ "status": 200 }],
      "errors": [{ "status": 404 }]
    }
  ]
}
```

---

### Stage 2: Intent Generation

*(Same as Pytest pipeline - see OPENAPI_TO_TESTSUITE.md)*

#### Output: Test Intents

```json
[
  { "intent": "HAPPY_PATH", "target": "inputs.body", "expected_status": "201" },
  { "intent": "REQUIRED_FIELD_MISSING", "field": "email", "expected_status": "422" },
  { "intent": "TYPE_VIOLATION", "field": "email", "expected_status": "422" },
  { "intent": "SQL_INJECTION", "field": "name", "expected_status": "422" }
]
```

---

### Stage 3: Payload Generation

*(Same as Pytest pipeline - see OPENAPI_TO_TESTSUITE.md)*

#### Output: Test Payloads

```json
[
  {
    "operation_id": "createUser",
    "intent": "HAPPY_PATH",
    "payload": { "email": "test@example.com", "name": "Test User" },
    "path_params": {},
    "expected_status": 201
  },
  {
    "operation_id": "createUser",
    "intent": "REQUIRED_FIELD_MISSING",
    "payload": { "name": "Test User" },
    "path_params": {},
    "expected_status": 422
  }
]
```

---

### Stage 4: LLM Enhancement (Optional)

*(Same as Pytest pipeline - see OPENAPI_TO_TESTSUITE.md)*

---

### Stage 5: Static Test Analysis

*(Same as Pytest pipeline - see OPENAPI_TO_TESTSUITE.md)*

---

### Stage 6: Setup/Teardown Generation

**File:** `testsuite/generator.py`

**Purpose:** Generate Jest-specific `beforeAll`/`afterAll` hooks.

#### Input: Setup Plan (from Stage 5 analysis)

```json
{
  "operation_id": "getUser",
  "needs_setup": true,
  "setup_steps": [{
    "resource_type": "user",
    "endpoint": "/users",
    "method": "POST",
    "payload": { "email": "test@example.com", "name": "Test User" }
  }]
}
```

#### Output: Jest Setup Code

```typescript
beforeAll(async () => {
  // Create user resource
  const createUserPayload = {
    email: `test_${Date.now()}@example.com`,
    name: "Test User"
  };

  const response = await fetch(`${BASE_URL}/users`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(createUserPayload),
  });

  if (response.ok) {
    const data = await response.json();
    const userId = data.id;
    placeholders["user_id"] = userId;
    placeholders["USE_CREATED_RESOURCE_user"] = userId;
    createdResources.push({
      type: "user",
      id: userId,
      endpoint: `/users/${userId}`,
    });
  }
});

afterAll(async () => {
  // Cleanup created resources in reverse order
  for (const resource of [...createdResources].reverse()) {
    try {
      await fetch(`${BASE_URL}${resource.endpoint}`, { method: "DELETE" });
    } catch {
      // Ignore cleanup errors
    }
  }
});
```

---

### Stage 7: Jest Test Rendering

**File:** `testsuite/templates.py` → `OPENAPI_JEST_TEST_TEMPLATE`

**Purpose:** Render final Jest test files using Jinja2 templates.

#### Input: All Components Combined

- IR operation metadata
- Test payloads
- Setup/teardown code
- Base URL configuration

#### Output: Complete Jest Test File

```typescript
// Uses native fetch (Node.js 18+)
// Auto-generated by TestSuiteGen - Setup is pre-compiled

describe("GET /users/{user_id} (getUser)", () => {
  const BASE_URL = "http://localhost:8000";
  const ENDPOINT = "/users/{user_id}";
  const METHOD: string = "GET";

  // Operation: getUser
  // Error Codes Expected: 404

  // Resource tracking for setup/teardown
  const createdResources: Array<{ type: string; id: any; endpoint: string }> = [];
  const placeholders: Record<string, any> = {};

  beforeAll(async () => {
    // Create user resource
    const createUserPayload = {
      email: `test_${Date.now()}@example.com`,
      name: "Test User",
    };

    const response = await fetch(`${BASE_URL}/users`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(createUserPayload),
    });

    if (response.ok) {
      const data = await response.json();
      placeholders["user_id"] = data.id;
      placeholders["USE_CREATED_RESOURCE_user"] = data.id;
      createdResources.push({
        type: "user",
        id: data.id,
        endpoint: `/users/${data.id}`,
      });
    }
  });

  afterAll(async () => {
    for (const resource of [...createdResources].reverse()) {
      try {
        await fetch(`${BASE_URL}${resource.endpoint}`, { method: "DELETE" });
      } catch {
        // Ignore cleanup errors
      }
    }
  });

  const testCases = [
    {
      intent: "HAPPY_PATH",
      payload: {},
      pathParams: { user_id: "USE_CREATED_RESOURCE_user" },
      expectedStatus: 200,
    },
    {
      intent: "RESOURCE_NOT_FOUND",
      payload: {},
      pathParams: { user_id: "550e8400-e29b-41d4-a716-446655440000" },
      expectedStatus: 404,
    },
    {
      intent: "FORMAT_INVALID_PATH_PARAM",
      payload: {},
      pathParams: { user_id: "not-a-valid-uuid" },
      expectedStatus: 422,
    },
  ];

  it.each(testCases)("intent: %s", async (testCase) => {
    const { intent, payload, pathParams, expectedStatus } = testCase;

    let url = `${BASE_URL}${ENDPOINT}`;

    // Resolve USE_CREATED_RESOURCE placeholders
    const resolvedParams: Record<string, any> = { ...pathParams };
    for (const [name, value] of Object.entries(resolvedParams)) {
      if (typeof value === "string" && value.startsWith("USE_CREATED_RESOURCE")) {
        const resolved = placeholders[value] ?? createdResources[0]?.id ?? null;
        if (resolved === null) {
          console.warn(`Skipping test: placeholder ${value} not resolved`);
          return;
        }
        resolvedParams[name] = resolved;
      }
    }

    // Replace path parameters in URL
    for (const [name, value] of Object.entries(resolvedParams)) {
      const paramValue =
        value === "__INVALID_TYPE__" ? "invalid_string_value" : value ?? 1;
      url = url
        .replace(`:${name}`, String(paramValue))
        .replace(`{${name}}`, String(paramValue));
    }

    const init: RequestInit = {
      method: METHOD,
      headers: { "Content-Type": "application/json" },
    };

    // Only attach body for methods that support it
    if (payload && ["POST", "PUT", "PATCH"].includes(METHOD)) {
      init.body = JSON.stringify(payload);
    }

    const response = await fetch(url, init);

    expect(response.status).toBe(expectedStatus);

    if (expectedStatus >= 400) {
      try {
        const body = await response.json();
        expect(body).toBeDefined();
      } catch {
        // Some error responses might not have JSON body
      }
    }
  });
});

export {};
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
│   - Resolves $ref references              │
│   - Normalizes schemas                    │
│   - Extracts all operations               │
└───────────────────────────────────────────┘
                │
                ▼ IR (JSON)
┌───────────────────────────────────────────┐
│ Stage 2: Intent Generator                 │
│   - HAPPY_PATH                            │
│   - REQUIRED_FIELD_MISSING                │
│   - BOUNDARY_*, SQL_INJECTION, etc.       │
└───────────────────────────────────────────┘
                │
                ▼ Intents (List)
┌───────────────────────────────────────────┐
│ Stage 3: Payload Generator                │
│   - Builds Golden Record                  │
│   - Applies mutations per intent          │
└───────────────────────────────────────────┘
                │
                ▼ Payloads (List)
┌───────────────────────────────────────────┐
│ Stage 4: LLM Enhancement (Optional)       │
│   - Replaces placeholders                 │
│   - Adds realistic test data              │
└───────────────────────────────────────────┘
                │
                ▼ Enhanced Payloads
┌───────────────────────────────────────────┐
│ Stage 5: Static Test Analyzer             │
│   - Detects resource dependencies         │
│   - Maps POST → GET/DELETE relationships  │
└───────────────────────────────────────────┘
                │
                ▼ Analysis Results
┌───────────────────────────────────────────┐
│ Stage 6: Jest Setup Generator             │
│   - beforeAll() hook                      │
│   - afterAll() cleanup                    │
│   - Placeholder resolution                │
└───────────────────────────────────────────┘
                │
                ▼ Setup/Teardown Code
┌───────────────────────────────────────────┐
│ Stage 7: Jest Template Renderer           │
│   - OPENAPI_JEST_TEST_TEMPLATE            │
│   - it.each() parameterization            │
│   - TypeScript types                      │
└───────────────────────────────────────────┘
                │
                ▼
OUTPUT: getUser.test.ts, createUser.test.ts, ...
```

---

## Jest-Specific Features

### Native Fetch API

Jest tests use Node.js 18+ native `fetch`:

```typescript
const response = await fetch(url, {
  method: METHOD,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});
```

### Parameterized Tests with `it.each()`

```typescript
const testCases = [
  { intent: "HAPPY_PATH", payload: {...}, expectedStatus: 200 },
  { intent: "VALIDATION_ERROR", payload: {...}, expectedStatus: 422 },
];

it.each(testCases)("intent: %s", async (testCase) => {
  // Test logic
});
```

### TypeScript Type Annotations

```typescript
const createdResources: Array<{ type: string; id: any; endpoint: string }> = [];
const placeholders: Record<string, any> = {};
const resolvedParams: Record<string, any> = { ...pathParams };
```

### Placeholder Resolution

```typescript
// Resolve USE_CREATED_RESOURCE placeholders
for (const [name, value] of Object.entries(resolvedParams)) {
  if (typeof value === "string" && value.startsWith("USE_CREATED_RESOURCE")) {
    const resolved = placeholders[value] ?? createdResources[0]?.id ?? null;
    resolvedParams[name] = resolved;
  }
}
```

### Path Parameter Substitution

```typescript
// Replace both :param and {param} styles
url = url
  .replace(`:${name}`, String(paramValue))
  .replace(`{${name}}`, String(paramValue));
```

---

## Comparison: Pytest vs Jest

| Feature | Pytest | Jest |
|---------|--------|------|
| Language | Python | TypeScript |
| HTTP Client | `requests.Session` | Native `fetch` |
| Fixtures | `@pytest.fixture` | `beforeAll`/`afterAll` |
| Parameterization | `@pytest.mark.parametrize` | `it.each()` |
| Test Structure | Class-based or function-based | `describe`/`it` blocks |
| Assertions | `assert` | `expect().toBe()` |
| Async | Implicit | `async`/`await` |

---

## Running Generated Tests

```bash
# Install dependencies
npm install --save-dev jest @types/jest ts-jest typescript

# Configure Jest (jest.config.js)
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
};

# Run tests
npx jest --verbose
```

---

## Summary

The OpenAPI to Jest pipeline produces:

1. **Type-Safe Tests** - Full TypeScript with proper type annotations
2. **Native Fetch** - No external HTTP library dependencies
3. **Automatic Setup** - `beforeAll` creates prerequisite resources
4. **Automatic Cleanup** - `afterAll` removes created resources
5. **Data-Driven** - `it.each()` for comprehensive coverage
6. **Ready to Run** - Works immediately with `npx jest`

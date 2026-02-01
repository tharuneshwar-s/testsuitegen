# TypeScript Function to Jest Test Suite

A comprehensive guide to how TestSuiteGen transforms TypeScript function definitions into Jest test suites.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Pipeline Stages](#pipeline-stages)
   - [Stage 1: Tree-sitter Parsing](#stage-1-tree-sitter-parsing)
   - [Stage 2: Intent Generation](#stage-2-intent-generation)
   - [Stage 3: Payload Generation](#stage-3-payload-generation)
   - [Stage 4: LLM Enhancement (Optional)](#stage-4-llm-enhancement-optional)
   - [Stage 5: Jest Generation](#stage-5-jest-generation)
4. [Complete Example](#complete-example)
5. [Supported TypeScript Features](#supported-typescript-features)

---

## Overview

TestSuiteGen parses TypeScript source code using Tree-sitter to extract function signatures and type annotations, then generates comprehensive Jest test suites.

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  TypeScript     │────▶│    IR (JSON)    │────▶│   Test Intents  │
│   (.ts file)    │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Jest File      │◀────│  Template       │◀────│   Test Payloads │
│  (*.test.ts)    │     │  Rendering      │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## Architecture

```
testsuitegen/src/
├── parsers/
│   └── typescript_parser/
│       └── parser.py              # Stage 1: TypeScript → IR
├── generators/
│   ├── intent_generator/
│   │   └── typescript_intent/
│   │       └── generator.py       # Stage 2: IR → Intents
│   └── payloads_generator/
│       ├── generator.py           # Stage 3: Intents → Payloads
│       └── typescript_mutator/
│           └── mutator.py         # TypeScript-specific mutations
├── llm_enhancer/
│   └── typescript_enhancer/
│       └── enhancer.py            # Stage 4: Optional enhancement
└── testsuite/
    ├── generator.py               # Stage 5: Test generation
    └── templates.py               # TYPESCRIPT_FUNCTION_TEST_TEMPLATE
```

---

## Pipeline Stages

### Stage 1: Tree-sitter Parsing

**File:** `parsers/typescript_parser/parser.py`

**Purpose:** Convert TypeScript source code into an Intermediate Representation (IR) using Tree-sitter for accurate AST parsing.

#### Input: TypeScript Source Code

```typescript
// user.ts
export enum UserStatus {
  Active = "active",
  Inactive = "inactive",
  Pending = "pending"
}

export interface User {
  name: string;
  email: string;
  age: number;
  status: UserStatus;
}

export interface CreateUserOptions {
  tags?: string[];
  sendWelcomeEmail?: boolean;
}

/**
 * Creates a new user with validation.
 * 
 * @param name - User's full name (1-100 chars)
 * @param email - Valid email address
 * @param age - User's age (must be positive)
 * @param status - Account status
 * @param options - Optional configuration
 * @returns The created user object
 * @throws {ValidationError} If validation fails
 */
export function createUser(
  name: string,
  email: string,
  age: number,
  status: UserStatus = UserStatus.Pending,
  options?: CreateUserOptions
): User {
  if (!name || name.length > 100) {
    throw new ValidationError("Name must be 1-100 characters");
  }
  if (age < 0 || age > 150) {
    throw new ValidationError("Age must be between 0 and 150");
  }
  if (!email.includes("@")) {
    throw new ValidationError("Invalid email format");
  }
  
  return { name, email, age, status };
}

export async function fetchUserById(id: string): Promise<User | null> {
  // Async function example
  const response = await fetch(`/api/users/${id}`);
  if (!response.ok) return null;
  return response.json();
}
```

#### Parsing Process

1. **Tree-sitter Parse** - Parse TypeScript into concrete syntax tree
2. **First Pass** - Extract all type definitions (enums, interfaces, type aliases)
3. **Second Pass** - Extract all function declarations
4. **Type Resolution** - Convert TypeScript types to JSON Schema

#### Output: Intermediate Representation (IR)

```json
{
  "operations": [
    {
      "id": "createUser",
      "kind": "function",
      "async": false,
      "description": "Creates a new user with validation...",
      "metadata": {
        "decorators": [],
        "exported": true
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
                "type": "number"
              },
              "status": {
                "type": "string",
                "enum": ["active", "inactive", "pending"],
                "x-enum-type": "UserStatus"
              },
              "options": {
                "type": "object",
                "x-interface-type": "CreateUserOptions",
                "nullable": true,
                "properties": {
                  "tags": {
                    "type": "array",
                    "items": { "type": "string" },
                    "nullable": true
                  },
                  "sendWelcomeEmail": {
                    "type": "boolean",
                    "nullable": true
                  }
                }
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
            "x-interface-type": "User"
          }
        }
      ],
      "errors": []
    },
    {
      "id": "fetchUserById",
      "kind": "function",
      "async": true,
      "description": "",
      "metadata": {
        "decorators": [],
        "exported": true
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
              "id": { "type": "string" }
            },
            "required": ["id"],
            "additionalProperties": false
          }
        }
      },
      "outputs": [
        {
          "status": 200,
          "content_type": "application/json",
          "schema": {
            "oneOf": [
              { "type": "object", "x-interface-type": "User" },
              { "type": "null" }
            ]
          }
        }
      ],
      "errors": []
    }
  ],
  "types": [
    {
      "id": "UserStatus",
      "kind": "enum",
      "description": "",
      "values": [
        { "name": "Active", "value": "active" },
        { "name": "Inactive", "value": "inactive" },
        { "name": "Pending", "value": "pending" }
      ]
    },
    {
      "id": "User",
      "kind": "interface",
      "description": "",
      "schema": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string" },
          "age": { "type": "number" },
          "status": { "x-enum-type": "UserStatus" }
        },
        "required": ["name", "email", "age", "status"]
      }
    },
    {
      "id": "CreateUserOptions",
      "kind": "interface",
      "description": "",
      "schema": {
        "type": "object",
        "properties": {
          "tags": {
            "type": "array",
            "items": { "type": "string" },
            "nullable": true
          },
          "sendWelcomeEmail": {
            "type": "boolean",
            "nullable": true
          }
        },
        "required": []
      }
    }
  ]
}
```

#### TypeScript to JSON Schema Mapping

| TypeScript Type | JSON Schema |
|-----------------|-------------|
| `string` | `{"type": "string"}` |
| `number` | `{"type": "number"}` |
| `boolean` | `{"type": "boolean"}` |
| `null` | `{"type": "null"}` |
| `string[]` / `Array<string>` | `{"type": "array", "items": {"type": "string"}}` |
| `Record<string, T>` | `{"type": "object", "additionalProperties": {...}}` |
| `T \| null` | `{"oneOf": [{...}, {"type": "null"}]}` |
| `T \| undefined` | `{..., "nullable": true}` |
| `T?` (optional) | `{..., "nullable": true}` |
| `A \| B \| C` | `{"oneOf": [{...}, {...}, {...}]}` |
| `"a" \| "b" \| "c"` (literal) | `{"enum": ["a", "b", "c"]}` |
| `enum E {...}` | `{"type": "string", "enum": [...], "x-enum-type": "E"}` |
| `interface I {...}` | `{"type": "object", "x-interface-type": "I", ...}` |
| `T<U>` (generic) | Resolved with constraints |
| `Promise<T>` | Schema of `T` (unwrapped) |

---

### Stage 2: Intent Generation

**File:** `generators/intent_generator/typescript_intent/generator.py`

**Purpose:** Analyze the IR schema and generate test intents specific to TypeScript.

#### Input: Single IR Operation

```json
{
  "id": "createUser",
  "kind": "function",
  "async": false,
  "inputs": {
    "body": {
      "schema": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "email": { "type": "string" },
          "age": { "type": "number" },
          "status": { "type": "string", "enum": ["active", "inactive", "pending"] },
          "options": { "type": "object", "nullable": true }
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
    "intent": "UNDEFINED_NOT_ALLOWED",
    "target": "body.name",
    "field": "name",
    "expected": "400",
    "description": "undefined passed to required argument: name"
  },
  {
    "intent": "NULL_NOT_ALLOWED",
    "target": "body.name",
    "field": "name",
    "expected": "400",
    "description": "null passed to non-nullable argument: name"
  },
  {
    "intent": "ENUM_MISMATCH",
    "target": "body.status",
    "field": "status",
    "expected": "400",
    "description": "Invalid enum value for: status"
  },
  {
    "intent": "INTERFACE_MISSING_PROPERTY",
    "target": "body.options",
    "field": "options",
    "expected": "400",
    "description": "Interface missing required property"
  },
  {
    "intent": "UNION_NO_MATCH",
    "target": "body.status",
    "field": "status",
    "expected": "400",
    "description": "Value doesn't match any union variant"
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

#### TypeScript-Specific Intent Categories

| Category | Intent Types | Description |
|----------|--------------|-------------|
| **Functional** | `HAPPY_PATH` | Valid function call |
| **Structural** | `REQUIRED_ARG_MISSING`, `UNEXPECTED_ARGUMENT` | Argument structure |
| **Type** | `TYPE_VIOLATION`, `NULL_NOT_ALLOWED`, `UNDEFINED_NOT_ALLOWED` | Type validation |
| **Union** | `UNION_NO_MATCH` | Union type matching |
| **Interface** | `INTERFACE_MISSING_PROPERTY` | Interface compliance |
| **Generics** | `GENERIC_TYPE_VIOLATION` | Generic constraint violation |
| **Enum** | `ENUM_MISMATCH` | Enum value validation |
| **Array** | `ARRAY_ITEM_TYPE_VIOLATION` | Array item types |
| **Security** | `SQL_INJECTION`, `XSS_INJECTION` | Security fuzzing |

---

### Stage 3: Payload Generation

**File:** `generators/payloads_generator/typescript_mutator/mutator.py`

**Purpose:** Transform intents into concrete test payloads (function arguments).

#### Input: Intent + Schema

```json
{
  "intent": "TYPE_VIOLATION",
  "target": "body.age",
  "field": "age",
  "expected": "400"
}
```

#### Process: Golden Record Mutation

1. **Build Golden Record** - Create valid arguments from schema
2. **Apply Mutation** - Modify based on intent
3. **Return Payload** - Complete test case

```typescript
// Golden Record (valid arguments)
{
    name: "__PLACEHOLDER_STRING_name__",
    email: "__PLACEHOLDER_STRING_email__",
    age: 1,
    status: "active"
}

// After TYPE_VIOLATION mutation for 'age'
{
    name: "__PLACEHOLDER_STRING_name__",
    email: "__PLACEHOLDER_STRING_email__",
    age: "__INVALID_TYPE__",  // string instead of number
    status: "active"
}
```

#### Output: Test Payloads

```json
[
  {
    "operation_id": "createUser",
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
    "operation_id": "createUser",
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
    "operation_id": "createUser",
    "intent": "TYPE_VIOLATION",
    "field": "age",
    "expected_status": 400,
    "payload": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": "not_a_number",
      "status": "active"
    }
  },
  {
    "operation_id": "createUser",
    "intent": "NULL_NOT_ALLOWED",
    "field": "name",
    "expected_status": 400,
    "payload": {
      "name": null,
      "email": "john@example.com",
      "age": 25,
      "status": "active"
    }
  },
  {
    "operation_id": "createUser",
    "intent": "UNDEFINED_NOT_ALLOWED",
    "field": "name",
    "expected_status": 400,
    "payload": {
      "email": "john@example.com",
      "age": 25,
      "status": "active"
    }
  },
  {
    "operation_id": "createUser",
    "intent": "ENUM_MISMATCH",
    "field": "status",
    "expected_status": 400,
    "payload": {
      "name": "John Doe",
      "email": "john@example.com",
      "age": 25,
      "status": "invalid_status"
    }
  }
]
```

#### TypeScript Mutation Strategies

| Intent | Mutation Applied |
|--------|------------------|
| `REQUIRED_ARG_MISSING` | Remove the argument |
| `UNDEFINED_NOT_ALLOWED` | Set to `undefined` (omit key) |
| `NULL_NOT_ALLOWED` | Set to `null` |
| `TYPE_VIOLATION` | Set to wrong type value |
| `ENUM_MISMATCH` | Set to invalid enum string |
| `UNION_NO_MATCH` | Set to value matching no variant |
| `INTERFACE_MISSING_PROPERTY` | Object missing required props |
| `ARRAY_ITEM_TYPE_VIOLATION` | Array with wrong item types |
| `GENERIC_TYPE_VIOLATION` | Value violates generic constraint |
| `SQL_INJECTION` | Set to `' OR '1'='1` |
| `XSS_INJECTION` | Set to `<script>alert(1)</script>` |

---

### Stage 4: LLM Enhancement (Optional)

**File:** `llm_enhancer/typescript_enhancer/enhancer.py`

**Purpose:** Replace placeholder values with realistic test data.

#### Input: Payload with Placeholders

```typescript
{
    name: "__PLACEHOLDER_STRING_name__",
    email: "__PLACEHOLDER_STRING_email__",
    age: 1
}
```

#### Output: Enhanced Payload

```typescript
{
    name: "John Doe",
    email: "john.doe@example.com",
    age: 28
}
```

---

### Stage 5: Jest Generation

**File:** `testsuite/generator.py` + `templates.py`

**Purpose:** Render final Jest test files using Jinja2 templates.

#### Input: All Components

- IR operation
- Test payloads
- Enum/interface types for imports
- Module path

#### Template: TYPESCRIPT_FUNCTION_TEST_TEMPLATE

```typescript
import { {{ function_name }}{% if enum_imports %}, {{ enum_imports | join(', ') }}{% endif %} } from '{{ module_path }}';

// Auto-generated by TestSuiteGen
// Function: {{ function_name }}

describe('{{ function_name }}', () => {
  {% for group_name, test_cases in grouped_tests.items() %}
  describe('{{ group_name }}', () => {
    it.each([
      {% for tc in test_cases %}
      {
        intent: '{{ tc.intent }}',
        args: {{ tc.args | tojson }},
        expectedStatus: {{ tc.expected_status }}
      },
      {% endfor %}
    ])('$intent', {% if is_async %}async {% endif %}({ intent, args, expectedStatus }) => {
      {% if has_negative_tests %}
      if (expectedStatus >= 400) {
        {% if is_async %}
        await expect({{ function_name }}(
          {% for arg_name in arg_names %}args.{{ arg_name }}{{ ", " if not loop.last else "" }}{% endfor %}
        )).rejects.toThrow();
        {% else %}
        expect(() => {{ function_name }}(
          {% for arg_name in arg_names %}args.{{ arg_name }}{{ ", " if not loop.last else "" }}{% endfor %}
        )).toThrow();
        {% endif %}
      } else {
      {% endif %}
        const result = {% if is_async %}await {% endif %}{{ function_name }}(
          {% for arg_name in arg_names %}args.{{ arg_name }}{{ ", " if not loop.last else "" }}{% endfor %}
        );
        expect(result).toBeDefined();
      {% if has_negative_tests %}
      }
      {% endif %}
    });
  });
  {% endfor %}
});
```

#### Output: Complete Jest Test File

```typescript
import { createUser, UserStatus } from './user';

// Auto-generated by TestSuiteGen
// Function: createUser

describe('createUser', () => {
  describe('Functional Tests', () => {
    it.each([
      {
        intent: 'HAPPY_PATH',
        args: { name: 'John Doe', email: 'john@example.com', age: 25, status: 'active' },
        expectedStatus: 200
      },
    ])('$intent', ({ intent, args, expectedStatus }) => {
      if (expectedStatus >= 400) {
        expect(() => createUser(args.name, args.email, args.age, args.status as UserStatus)).toThrow();
      } else {
        const result = createUser(args.name, args.email, args.age, args.status as UserStatus);
        expect(result).toBeDefined();
        expect(result.name).toBe(args.name);
      }
    });
  });

  describe('Structural Tests', () => {
    it.each([
      {
        intent: 'REQUIRED_ARG_MISSING_name',
        args: { email: 'john@example.com', age: 25, status: 'active' },
        expectedStatus: 400
      },
      {
        intent: 'REQUIRED_ARG_MISSING_email',
        args: { name: 'John Doe', age: 25, status: 'active' },
        expectedStatus: 400
      },
      {
        intent: 'REQUIRED_ARG_MISSING_age',
        args: { name: 'John Doe', email: 'john@example.com', status: 'active' },
        expectedStatus: 400
      },
    ])('$intent', ({ intent, args, expectedStatus }) => {
      if (expectedStatus >= 400) {
        expect(() => createUser(
          args.name as any,
          args.email as any,
          args.age as any,
          args.status as UserStatus
        )).toThrow();
      }
    });
  });

  describe('Type Violation Tests', () => {
    it.each([
      {
        intent: 'TYPE_VIOLATION_name',
        args: { name: 12345, email: 'john@example.com', age: 25, status: 'active' },
        expectedStatus: 400
      },
      {
        intent: 'TYPE_VIOLATION_age',
        args: { name: 'John Doe', email: 'john@example.com', age: 'not_a_number', status: 'active' },
        expectedStatus: 400
      },
      {
        intent: 'NULL_NOT_ALLOWED_name',
        args: { name: null, email: 'john@example.com', age: 25, status: 'active' },
        expectedStatus: 400
      },
    ])('$intent', ({ intent, args, expectedStatus }) => {
      expect(() => createUser(
        args.name as any,
        args.email as any,
        args.age as any,
        args.status as UserStatus
      )).toThrow();
    });
  });

  describe('Enum Tests', () => {
    it.each([
      {
        intent: 'ENUM_MISMATCH_status',
        args: { name: 'John Doe', email: 'john@example.com', age: 25, status: 'invalid_status' },
        expectedStatus: 400
      },
    ])('$intent', ({ intent, args, expectedStatus }) => {
      expect(() => createUser(
        args.name,
        args.email,
        args.age,
        args.status as UserStatus
      )).toThrow();
    });
  });

  describe('Security Tests', () => {
    it.each([
      {
        intent: 'SQL_INJECTION_name',
        args: { name: "' OR '1'='1", email: 'john@example.com', age: 25, status: 'active' },
        expectedStatus: 400
      },
      {
        intent: 'XSS_INJECTION_email',
        args: { name: 'John Doe', email: '<script>alert(1)</script>', age: 25, status: 'active' },
        expectedStatus: 400
      },
    ])('$intent', ({ intent, args, expectedStatus }) => {
      expect(() => createUser(
        args.name,
        args.email,
        args.age,
        args.status as UserStatus
      )).toThrow();
    });
  });
});
```

#### Async Function Handling

For async functions like `fetchUserById`:

```typescript
import { fetchUserById } from './user';

describe('fetchUserById', () => {
  describe('Functional Tests', () => {
    it.each([
      {
        intent: 'HAPPY_PATH',
        args: { id: '123' },
        expectedStatus: 200
      },
    ])('$intent', async ({ intent, args, expectedStatus }) => {
      if (expectedStatus >= 400) {
        await expect(fetchUserById(args.id)).rejects.toThrow();
      } else {
        const result = await fetchUserById(args.id);
        // Result can be User | null, so we just check it doesn't throw
        expect(result === null || typeof result === 'object').toBe(true);
      }
    });
  });

  describe('Type Violation Tests', () => {
    it.each([
      {
        intent: 'TYPE_VIOLATION_id',
        args: { id: 12345 },  // number instead of string
        expectedStatus: 400
      },
    ])('$intent', async ({ intent, args, expectedStatus }) => {
      await expect(fetchUserById(args.id as any)).rejects.toThrow();
    });
  });
});
```

---

## Complete Example

### End-to-End Flow

```
INPUT: user.ts (TypeScript Source)
                │
                ▼
┌───────────────────────────────────────────┐
│ Stage 1: Tree-sitter Parser              │
│   - Parse with tree_sitter_typescript    │
│   - Extract enums & interfaces           │
│   - Extract function declarations        │
│   - Resolve type references              │
└───────────────────────────────────────────┘
                │
                ▼ IR (JSON)
┌───────────────────────────────────────────┐
│ Stage 2: TypeScript Intent Generator     │
│   - HAPPY_PATH                           │
│   - REQUIRED_ARG_MISSING (per required)  │
│   - TYPE_VIOLATION (per argument)        │
│   - NULL/UNDEFINED_NOT_ALLOWED           │
│   - ENUM_MISMATCH, UNION_NO_MATCH        │
│   - Security tests                       │
└───────────────────────────────────────────┘
                │
                ▼ Intents (List)
┌───────────────────────────────────────────┐
│ Stage 3: TypeScript Payload Generator    │
│   - Uses TypeScriptMutator               │
│   - Builds Golden Record                 │
│   - Applies mutations per intent         │
└───────────────────────────────────────────┘
                │
                ▼ Payloads (List)
┌───────────────────────────────────────────┐
│ Stage 4: LLM Enhancement (Optional)      │
│   - Replaces placeholders                │
│   - Adds realistic values                │
└───────────────────────────────────────────┘
                │
                ▼ Enhanced Payloads
┌───────────────────────────────────────────┐
│ Stage 5: Jest Generator                  │
│   - TYPESCRIPT_FUNCTION_TEST_TEMPLATE    │
│   - describe/it.each pattern             │
│   - Async/await support                  │
│   - expect().toThrow() for errors        │
│   - .rejects.toThrow() for async errors  │
└───────────────────────────────────────────┘
                │
                ▼
OUTPUT: user.test.ts
```

---

## Supported TypeScript Features

### Type Annotations

| Feature | Example | Supported |
|---------|---------|-----------|
| Primitive types | `string`, `number`, `boolean` | ✅ |
| null/undefined | `null`, `undefined` | ✅ |
| Arrays | `string[]`, `Array<number>` | ✅ |
| Tuples | `[string, number]` | ✅ |
| Objects | `{ key: string }` | ✅ |
| Union types | `string \| number` | ✅ |
| Literal types | `"a" \| "b" \| "c"` | ✅ |
| Optional | `name?: string` | ✅ |
| Record | `Record<string, T>` | ✅ |
| Generics | `T extends Base` | Partial |
| Mapped types | `Partial<T>`, `Required<T>` | Partial |
| Conditional | `T extends U ? X : Y` | ❌ |

### Type Definitions

| Feature | Example | Supported |
|---------|---------|-----------|
| Enums | `enum Status { Active }` | ✅ |
| Const enums | `const enum Status { }` | ✅ |
| String enums | `enum S { A = "a" }` | ✅ |
| Numeric enums | `enum N { A = 1 }` | ✅ |
| Interfaces | `interface User { }` | ✅ |
| Type aliases | `type UserId = string` | ✅ |
| Classes | `class User { }` | ✅ |
| Generic interfaces | `interface Box<T> { }` | ✅ |

### Functions

| Feature | Example | Supported |
|---------|---------|-----------|
| Regular functions | `function fn(x: string)` | ✅ |
| Arrow functions | `const fn = (x: string) => {}` | ✅ |
| Async functions | `async function fn()` | ✅ |
| Default values | `function fn(x = 10)` | ✅ |
| Optional params | `function fn(x?: string)` | ✅ |
| Rest params | `function fn(...args: string[])` | ❌ |
| Overloads | Multiple signatures | ❌ |
| Generic functions | `function fn<T>(x: T)` | Partial |
| Return type | `: User` | ✅ |
| Promise return | `: Promise<User>` | ✅ |

---

## Running Generated Tests

```bash
# Run all generated tests
npx jest generated_tests/ --verbose

# Run specific test file
npx jest generated_tests/user.test.ts

# Run with coverage
npx jest generated_tests/ --coverage

# Watch mode
npx jest generated_tests/ --watch
```

---

## Jest Configuration

Ensure your `jest.config.js` supports TypeScript:

```javascript
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/*.test.ts'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
  transform: {
    '^.+\\.tsx?$': 'ts-jest',
  },
};
```

---

## Summary

The TypeScript Function to Jest pipeline produces:

1. **Type-Aware Tests** - Leverages TypeScript type annotations for comprehensive testing
2. **Union/Interface Support** - Tests union types and interface compliance
3. **Async Support** - Proper `async/await` handling with `.rejects.toThrow()`
4. **Enum Testing** - Validates enum values and rejects invalid ones
5. **Data-Driven** - Uses `it.each()` for parameterized tests
6. **Grouped by Intent** - Organized into describe blocks by test category
7. **Ready to Run** - Works immediately with Jest + ts-jest

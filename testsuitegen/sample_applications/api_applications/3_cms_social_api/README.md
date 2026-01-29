# CMS & Social API

A realistic sample application simulating a Content Management System to test **String Constraints**, **Enums**, and **Security** intents.

## UI Intent Selection

When generating tests for this application in the UI, select the following intents:

- **Standard Validation:**
  - `HAPPY_PATH`
  - `REQUIRED_FIELD_MISSING`
  - `msg_null_value`
- **String Constraints:**
  - `BOUNDARY_MIN_LENGTH_MINUS_ONE`
  - `BOUNDARY_MAX_LENGTH_PLUS_ONE`
  - `PATTERN_MISMATCH`
  - `FORMAT_INVALID`
  - `WHITESPACE_ONLY`
- **Enums:**
  - `ENUM_MISMATCH`
- **Security:**
  - `SQL_INJECTION`
  - `XSS_INJECTION`

## Endpoints & Expected Intents

### 1. `POST /users/profile` (String Constraints)

- **Endpoint Goal**: Create a user profile with strict validation.
- **Fields**:
  - `username` (String, min:3, max:20, pattern: `^[a-zA-Z0-9_]+$`)
  - `email` (String, format: `email`)
  - `bio` (String, max:500, optional)

| Field       | Intent                          | Expected Status | Description          |
| :---------- | :------------------------------ | :-------------- | :------------------- |
| `username`  | `REQUIRED_FIELD_MISSING`        | 422             | Missing field        |
| `username`  | `BOUNDARY_MIN_LENGTH_MINUS_ONE` | 422             | Length 2 < 3         |
| `username`  | `BOUNDARY_MAX_LENGTH_PLUS_ONE`  | 422             | Length 21 > 20       |
| `username`  | `PATTERN_MISMATCH`              | 422             | Invalid characters   |
| `email`     | `FORMAT_INVALID`                | 422             | Invalid email format |
| `email`     | `REQUIRED_FIELD_MISSING`        | 422             | Missing field        |
| `full_name` | `REQUIRED_FIELD_MISSING`        | 422             | Missing field        |

**Note**: `TYPE_VIOLATION` is NOT expected for string fields.

---

### 2. `POST /posts/create` (Enums & Arrays)

- **Endpoint Goal**: Create a blog post with status and tags.
- **Fields**:
  - `status` (Enum: `DRAFT`, `PUBLISHED`, `ARCHIVED`)
  - `tags` (Array, minItems: 1, maxItems: 10)

| Field    | Intent                         | Expected Status | Description            |
| :------- | :----------------------------- | :-------------- | :--------------------- |
| `status` | `ENUM_MISMATCH`                | 422             | Value not in enum      |
| `status` | `TYPE_VIOLATION`               | 422             | Sending int/bool/array |
| `tags`   | `BOUNDARY_MIN_ITEMS_MINUS_ONE` | 422             | Empty array (0 items)  |
| `tags`   | `BOUNDARY_MAX_ITEMS_PLUS_ONE`  | 422             | Array with 11 items    |

---

### 3. `POST /comments/add` (Security)

- **Endpoint Goal**: Add a comment (Unsafe input handling simulation).
- **Fields**:
  - `text` (String, no constraints)

| Field  | Intent            | Expected Status | Description                                |
| :----- | :---------------- | :-------------- | :----------------------------------------- |
| `text` | `XSS_INJECTION`   | 200             | Payload accepted (Simulated vulnerability) |
| `text` | `SQL_INJECTION`   | 200             | Payload accepted (Simulated vulnerability) |
| `text` | `WHITESPACE_ONLY` | 200             | Accepted unless minLength set              |

---

### 4. `GET /posts/search` (Query Injection)

- **Endpoint Goal**: Search posts.
- **Fields**:
  - `q` (Query Param, String)

| Field | Intent                   | Expected Status | Description                  |
| :---- | :----------------------- | :-------------- | :--------------------------- |
| `q`   | `SQL_INJECTION`          | 200             | Payload accepted             |
| `q`   | `REQUIRED_FIELD_MISSING` | 422             | Missing required query param |

---

## Running the App

```bash
cd testsuitegen/sample_applications/api_applications/3_cms_social_api
python main.py
# Server runs on http://0.0.0.0:8003
```

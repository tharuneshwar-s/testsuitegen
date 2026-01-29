# Fintech Transaction API

A realistic sample application simulating a Banking Service to test **Numeric Constraints**, **Boundaries**, and **Type Violations**.

## UI Intent Selection

When generating tests for this application in the UI, select the following intents:

- **Standard Validation:**
  - `HAPPY_PATH`
  - `REQUIRED_FIELD_MISSING`
  - `TYPE_VIOLATION` (Important for numeric fields)
  - `msg_null_value`
- **Numeric Constraints:**
  - `BOUNDARY_MIN_MINUS_ONE`
  - `BOUNDARY_MAX_PLUS_ONE`
  - `NOT_MULTIPLE_OF`

## Endpoints & Expected Intents

### 1. `POST /transfers/create` (Numeric Boundaries)

- **Endpoint Goal**: Transfer money between accounts.
- **Fields**:
  - `amount` (Float, >0, <=10000.00, multipleOf: 0.01)
  - `from_account` (Int, 10000-99999)
  - `to_account` (Int, 10000-99999)

| Field          | Intent                   | Expected Status | Description              |
| :------------- | :----------------------- | :-------------- | :----------------------- |
| `amount`       | `BOUNDARY_MIN_MINUS_ONE` | 422             | Value <= 0               |
| `amount`       | `BOUNDARY_MAX_PLUS_ONE`  | 422             | Value > 10000.00         |
| `amount`       | `NOT_MULTIPLE_OF`        | 422             | Value like 10.555        |
| `amount`       | `TYPE_VIOLATION`         | 422             | String instead of number |
| `from_account` | `BOUNDARY_MIN_MINUS_ONE` | 422             | Value 9999               |
| `from_account` | `BOUNDARY_MAX_PLUS_ONE`  | 422             | Value 100000             |
| `from_account` | `TYPE_VIOLATION`         | 422             | String instead of int    |

---

### 2. `POST /wallets/limit` (Integer Boundaries)

- **Endpoint Goal**: Update wallet limits.
- **Fields**:
  - `daily_limit` (Int, 0-5000)
  - `risk_score` (Float, 0.0-1.0)

| Field         | Intent                   | Expected Status | Description  |
| :------------ | :----------------------- | :-------------- | :----------- |
| `daily_limit` | `BOUNDARY_MIN_MINUS_ONE` | 422             | Value < 0    |
| `daily_limit` | `BOUNDARY_MAX_PLUS_ONE`  | 422             | Value > 5000 |
| `risk_score`  | `BOUNDARY_MIN_MINUS_ONE` | 422             | Value < 0.0  |
| `risk_score`  | `BOUNDARY_MAX_PLUS_ONE`  | 422             | Value > 1.0  |

---

## Running the App

```bash
cd testsuitegen/sample_applications/api_applications/4_fintech_api
python main.py
# Server runs on http://0.0.0.0:8004
```

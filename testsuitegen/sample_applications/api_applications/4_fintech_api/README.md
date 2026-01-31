# Fintech Transaction API ✅

A realistic sample application that simulates a small banking service — useful for exercising
numeric constraints, boundary conditions, schema validation and common REST error flows.

Highlights
- FastAPI-based in-memory demo (no external DB required)
- Clear intents focused on validation and resource lifecycle
- Designed for deterministic contract testing with TestSuiteGen

Quick facts
- Local server: http://0.0.0.0:8004
- Primary resources: users, transfers, wallets
- Background processing: transfers are processed asynchronously (status moves to `completed`)

---

## Quick start (run + smoke test) 🚀

1. Start the API:

```bash
cd testsuitegen/sample_applications/api_applications/4_fintech_api
python main.py
# listens on http://0.0.0.0:8004
```

2. Smoke-test with curl (happy path):

```bash
# create a user
curl -sS -X POST http://localhost:8004/users \
  -H 'Content-Type: application/json' \
  -d '{"name":"Alice","email":"alice@example.com","account_id":10001}'

# create a transfer (returns transfer id)
curl -sS -X POST http://localhost:8004/transfers/create \
  -H 'Content-Type: application/json' \
  -d '{"amount":10.50,"from_account":10001,"to_account":10002}'

# get transfer status (use returned id)
curl -sS http://localhost:8004/transfers/{transfer_id}
```

---

## Endpoints (summary + examples) 🔧

1) POST /users
- Purpose: create user
- Status: 201 on success
- Sample request body:
  {"name": "Alice", "email": "alice@example.com", "account_id": 10001}
- Error cases: missing fields, invalid email pattern, account_id out of range

2) GET /users/{user_id}
- Purpose: fetch user details
- Status: 200 (or 404 if not found)
- Note: generated GET contract tests will create the user automatically

3) POST /transfers/create
- Purpose: initiate a transfer (async processing)
- Status: 201 on success, returns {"id": "tx_...", "status": "pending", "amount": ...}
- Important validations: amount > 0, amount <= 10000.00, amount multipleOf 0.01, from/to account ranges
- Error examples: empty description -> 422, invalid amount types/values -> 422

4) GET /transfers/{transfer_id}
- Purpose: read transfer status (pending → completed after short background delay)
- Status: 200 or 404

5) POST /wallets/limit
- Purpose: update wallet limits
- Status: 200 on success
- Validations: daily_limit in [0,5000], risk_score in [0.0,1.0]

---

## Intents to use in the TestSuiteGen UI (recommended) 🎯

- Standard validation: `HAPPY_PATH`, `REQUIRED_FIELD_MISSING`, `TYPE_VIOLATION`
- Numeric constraints: `BOUNDARY_MIN_MINUS_ONE`, `BOUNDARY_MAX_PLUS_ONE`, `NOT_MULTIPLE_OF`
- Special checks: `RESOURCE_NOT_FOUND`, `EMPTY_STRING`, `FORMAT_INVALID`

Map of common intents → endpoints
- `POST /transfers/create`: numeric constraints, type violations, empty description
- `GET /users/{user_id}`: resource existence / not-found
- `POST /wallets/limit`: integer/float boundary checks

---

## Example payloads (copy/paste) 📋

Happy transfer:

```json
{ "amount": 25.50, "from_account": 10001, "to_account": 10002, "description": "test" }
```

Invalid transfer (not multiple of 0.01):

```json
{ "amount": 10.555, "from_account": 10001, "to_account": 10002 }
```

Wallet limit (happy):

```json
{ "daily_limit": 1000, "risk_score": 0.2 }
```

---

## Generating & running contract tests (TestSuiteGen) 🧪

1. Start this sample app (port 8004).
2. In TestSuiteGen UI choose this sample application and select the intents listed above.
3. Generate tests (the generator will produce pytest files under the artifacts/tests folder).
4. Run the generated tests against the running server:

```bash
# after generation, run pytest against the artifact tests folder (example path)
pytest <artifact_dir>/tests -q
```

Notes:
- The TestSuiteGen generator will automatically create prerequisite resources for GET/PUT/DELETE tests
  (you do not need to edit generated files).
- If a generated GET test uses the `USE_CREATED_RESOURCE` placeholder the test fixture will create the
  resource and replace the placeholder at runtime.

---

## Troubleshooting & tips ⚠️

- 404 on GET /users/{id}: ensure the fixture-created resource succeeded (check the test run logs for creation POST responses).
- 422 on POST /transfers/create (validation): inspect the JSON body for types/constraints (amount, account id ranges, empty strings).
- Transfer appears `pending` in tests: the background processor transitions to `completed` after ~2s; tests should poll/read status as needed.

---

## Development notes for maintainers 🛠

- This app is intentionally simple and deterministic (in-memory stores) to make contract tests stable.
- To extend behaviors, modify `main.py` in this folder and add corresponding intents/payloads to the TestSuiteGen dataset.

---

If you want, I can also add ready-to-run pytest examples (or a Postman collection) — tell me which format you prefer.

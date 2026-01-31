# Event Booking API - testsuitegen Demo

A simple FastAPI application demonstrating API contract testing with **testsuitegen**.

## Quick Start

```bash
# Start the API
uvicorn main:app --port 8006

# Run tests
cd tests && pytest -v
```

## Demo: Toggle Between BUGGY and FIXED Versions

Each endpoint has **PATCH comments** - uncomment the BUGGY version to see tests fail:

```python
# -------------------------------------------------------------------------
# PATCH: BUGGY VERSION (uncomment to see failing tests)
# -------------------------------------------------------------------------
# return events_db.get(event_id, {})  # BUG: No 404 for missing events
# -------------------------------------------------------------------------

# -------------------------------------------------------------------------
# PATCH: FIXED VERSION (current - tests pass)
# -------------------------------------------------------------------------
if event_id not in events_db:
    raise HTTPException(status_code=404, detail="Event not found")
return {"id": event_id, **events_db[event_id]}
# -------------------------------------------------------------------------
```

## Endpoints

| Method | Endpoint | Description | Intents Tested |
|--------|----------|-------------|----------------|
| GET | `/events` | List all events | HAPPY_PATH |
| GET | `/events/{id}` | Get event by ID | HAPPY_PATH, RESOURCE_NOT_FOUND |
| POST | `/events` | Create event | REQUIRED_FIELD_MISSING, TYPE_VIOLATION, ENUM_MISMATCH, PATTERN_MISMATCH, BOUNDARY_MIN/MAX |
| POST | `/bookings` | Create booking | HAPPY_PATH, REQUIRED_FIELD_MISSING, PATTERN_MISMATCH, BOUNDARY_MIN/MAX |
| GET | `/bookings/{id}` | Get booking | HAPPY_PATH, RESOURCE_NOT_FOUND |
| DELETE | `/bookings/{id}` | Cancel booking | HAPPY_PATH, RESOURCE_NOT_FOUND |

## Models

### Event
```python
{
    "title": str,       # 3-100 chars (STRING_TOO_SHORT/LONG)
    "event_type": enum, # conference|workshop|meetup (ENUM_MISMATCH)
    "capacity": int,    # 10-1000 (BOUNDARY_MIN/MAX)
    "price": float,     # 0-999.99, multiple of 0.01 (NOT_MULTIPLE_OF)
    "code": str         # Pattern: EVT-1234 (PATTERN_MISMATCH)
}
```

### Booking
```python
{
    "event_id": str,       # Required
    "attendee_name": str,  # 2-50 chars
    "attendee_email": str, # Email pattern
    "quantity": int        # 1-10
}
```

## Intents Covered

| Category | Intent | Triggered By |
|----------|--------|--------------|
| **Functional** | HAPPY_PATH | Valid requests |
| **Structure** | REQUIRED_FIELD_MISSING | Missing required fields |
| | TYPE_VIOLATION | Wrong data types |
| | RESOURCE_NOT_FOUND | Non-existent IDs |
| **Constraints** | ENUM_MISMATCH | Invalid enum values |
| | PATTERN_MISMATCH | Invalid patterns (EVT-1234) |
| | BOUNDARY_MIN_MINUS_ONE | capacity=9 (min is 10) |
| | BOUNDARY_MAX_PLUS_ONE | capacity=1001 (max is 1000) |
| | NOT_MULTIPLE_OF | price=9.999 (must be 0.01 multiple) |
| | STRING_TOO_SHORT | title="" (min 3 chars) |
| | STRING_TOO_LONG | title with >100 chars |

## Running the Demo

1. **Start with FIXED version** (all tests pass):
   ```bash
   pytest -v  # All green ✓
   ```

2. **Uncomment BUGGY version** in `main.py`:
   - Find `PATCH: BUGGY VERSION` comment
   - Uncomment the buggy code
   - Comment out the `PATCH: FIXED VERSION` code

3. **Run tests again** (tests fail):
   ```bash
   pytest -v  # Red failures ✗
   ```

4. **Explain the bug** and fix it by reverting

## API Documentation

- Swagger UI: http://localhost:8006/docs
- ReDoc: http://localhost:8006/redoc
- OpenAPI JSON: http://localhost:8006/openapi.json

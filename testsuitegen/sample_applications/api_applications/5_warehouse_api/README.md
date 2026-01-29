# Warehouse Inventory API

A realistic sample application simulating a Logistics System to test **Array Constraints**, **Object Constraints**, and **Nested Structures**.

## UI Intent Selection

When generating tests for this application in the UI, select the following intents:

- **Standard Validation:**
  - `HAPPY_PATH`
  - `REQUIRED_FIELD_MISSING`
  - `TYPE_VIOLATION`
  - `msg_null_value`
- **Array Constraints:**
  - `BOUNDARY_MIN_ITEMS_MINUS_ONE`
  - `BOUNDARY_MAX_ITEMS_PLUS_ONE`
  - `ARRAY_NOT_UNIQUE`
  - `ARRAY_ITEM_TYPE_VIOLATION`
- **Object Constraints:**
  - `OBJECT_VALUE_TYPE_VIOLATION`
  - `ADDITIONAL_PROPERTY_NOT_ALLOWED`

## Endpoints & Expected Intents

### 1. `POST /shipments/bulk` (Arrays & Uniqueness)

- **Endpoint Goal**: Create a bulk shipment of items.
- **Fields**:
  - `items` (Array[Object], minItems: 1, maxItems: 50)
  - `tags` (Array[String], minItems: 1, maxItems: 5, uniqueItems: true)

| Field   | Intent                         | Expected Status | Description                     |
| :------ | :----------------------------- | :-------------- | :------------------------------ |
| `items` | `BOUNDARY_MIN_ITEMS_MINUS_ONE` | 422             | Empty list []                   |
| `items` | `BOUNDARY_MAX_ITEMS_PLUS_ONE`  | 422             | List with 51 items              |
| `items` | `ARRAY_ITEM_TYPE_VIOLATION`    | 422             | `["string"]` instead of objects |
| `tags`  | `ARRAY_NOT_UNIQUE`             | 422             | `["urgent", "urgent"]`          |
| `tags`  | `BOUNDARY_MIN_ITEMS_MINUS_ONE` | 422             | Empty list []                   |

---

### 2. `POST /products/specs` (Object Constraints)

- **Endpoint Goal**: Register strict product specifications.
- **Fields**:
  - `specs` (Object, additionalProperties: false)
    - `voltage` (Int, required)
    - `amperage` (Float, required)

| Field              | Intent                            | Expected Status | Description                         |
| :----------------- | :-------------------------------- | :-------------- | :---------------------------------- |
| `specs`            | `ADDITIONAL_PROPERTY_NOT_ALLOWED` | 422             | Sending `{..., "extra": 1}`         |
| `specs.voltage`    | `REQUIRED_FIELD_MISSING`          | 422             | Missing required field              |
| `specs.dimensions` | `OBJECT_VALUE_TYPE_VIOLATION`     | 422             | Sending list/string instead of dict |

---

## Running the App

```bash
cd testsuitegen/sample_applications/api_applications/5_warehouse_api
python main.py
# Server runs on http://0.0.0.0:8005
```

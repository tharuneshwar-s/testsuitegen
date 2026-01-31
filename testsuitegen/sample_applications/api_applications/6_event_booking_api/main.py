"""
Event Booking API - Simple Demo Application

A minimal FastAPI app for demonstrating testsuitegen with PATCH comments.
Toggle between BUGGY and FIXED versions for demo presentations.

Run: uvicorn main:app --port 8006
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uvicorn

app = FastAPI(
    title="Event Booking API",
    description="Simple event booking for testsuitegen demo",
    version="1.0.0",
)


# =============================================================================
# ENUMS - For ENUM_MISMATCH intent
# =============================================================================


class EventType(str, Enum):
    CONFERENCE = "conference"
    WORKSHOP = "workshop"
    MEETUP = "meetup"


# =============================================================================
# MODELS
# =============================================================================


class Event(BaseModel):
    """Event model with validation constraints."""

    # REQUIRED_FIELD_MISSING, STRING_TOO_SHORT/LONG
    title: str = Field(..., min_length=3, max_length=100)

    # ENUM_MISMATCH
    event_type: EventType

    # BOUNDARY_MIN/MAX (capacity: 10-1000)
    capacity: int = Field(..., ge=10, le=1000)

    # NOT_MULTIPLE_OF, NUMBER_TOO_SMALL/LARGE
    price: float = Field(..., ge=0, le=999.99, multiple_of=0.01)

    # PATTERN_MISMATCH (format: EVT-XXXX or CONF-XXXX where X is 4-8 digits)
    code: str = Field(..., pattern=r"^(EVT|CONF)-\d{4,8}$")


class Booking(BaseModel):
    """Booking model."""

    event_id: str = Field(..., min_length=1)
    attendee_name: str = Field(..., min_length=2, max_length=50)
    attendee_email: str = Field(..., pattern=r"^[\w.-]+@[\w.-]+\.\w+$")
    quantity: int = Field(..., ge=1, le=10)


# =============================================================================
# DATABASE
# =============================================================================

events_db = {
    "evt-001": {
        "title": "Tech Conference 2026",
        "event_type": "conference",
        "capacity": 500,
        "price": 99.99,
        "code": "EVT-2026",
        "bookings": 45,
    },
    "evt-002": {
        "title": "Python Workshop",
        "event_type": "workshop",
        "capacity": 50,
        "price": 29.99,
        "code": "EVT-1001",
        "bookings": 12,
    },
    # Pre-seeded event for test compatibility (matches generated test payloads)
    "EVT-1234": {
        "title": "Test Event",
        "event_type": "conference",
        "capacity": 100,
        "price": 49.99,
        "code": "EVT-1234",
        "bookings": 0,
    },
}

bookings_db = {}


# =============================================================================
# ENDPOINTS
# =============================================================================


@app.get("/events", tags=["Events"])
async def list_events():
    """
    List all events.

    **Intents**: HAPPY_PATH
    """
    return {"events": list(events_db.values()), "total": len(events_db)}


@app.get("/events/{event_id}", tags=["Events"])
async def get_event(event_id: str):
    """
    Get event by ID.

    **Intents**: HAPPY_PATH, RESOURCE_NOT_FOUND
    """
    # -------------------------------------------------------------------------
    # PATCH: BUGGY VERSION (uncomment to see failing tests)
    # -------------------------------------------------------------------------
    # BUG: Returns empty dict instead of 404 - causes RESOURCE_NOT_FOUND to fail
    # return events_db.get(event_id, {})
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # PATCH: FIXED VERSION (current - tests pass)
    # -------------------------------------------------------------------------
    if event_id not in events_db:
        raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
    return {"id": event_id, **events_db[event_id]}
    # -------------------------------------------------------------------------


@app.post("/events", status_code=201, tags=["Events"])
async def create_event(event: Event):
    """
    Create a new event.

    **Intents**: HAPPY_PATH, REQUIRED_FIELD_MISSING, TYPE_VIOLATION,
    ENUM_MISMATCH, PATTERN_MISMATCH, BOUNDARY_MIN/MAX, NOT_MULTIPLE_OF,
    STRING_TOO_SHORT, STRING_TOO_LONG
    """

    event_id = f"evt-{len(events_db) + 1:03d}"
    events_db[event_id] = {
        "title": event.title,
        "event_type": event.event_type.value,
        "capacity": event.capacity,
        "price": event.price,
        "code": event.code,
        "bookings": 0,
    }
    return {
        "id": event_id,
        "message": "Event created",
        "timestamp": datetime.now().isoformat(),
    }
    # -------------------------------------------------------------------------


@app.post("/bookings", status_code=201, tags=["Bookings"])
async def create_booking(booking: Booking):
    """
    Create a booking for an event.

    **Intents**: HAPPY_PATH, REQUIRED_FIELD_MISSING, PATTERN_MISMATCH,
    BOUNDARY_MIN/MAX, RESOURCE_NOT_FOUND
    """

    if booking.event_id not in events_db:
        raise HTTPException(
            status_code=404, detail=f"Event {booking.event_id} not found"
        )

    event = events_db[booking.event_id]
    if event["bookings"] + booking.quantity > event["capacity"]:
        raise HTTPException(status_code=422, detail="Event is fully booked")

    booking_id = f"bk-{len(bookings_db) + 1:03d}"
    bookings_db[booking_id] = {
        **booking.model_dump(),
        "status": "confirmed",
        "created_at": datetime.now().isoformat(),
    }
    events_db[booking.event_id]["bookings"] += booking.quantity

    return {
        "id": booking_id,
        "message": "Booking confirmed",
        "event_title": event["title"],
    }
    # -------------------------------------------------------------------------


@app.get("/bookings/{booking_id}", tags=["Bookings"])
async def get_booking(booking_id: str):
    """
    Get booking by ID.

    **Intents**: HAPPY_PATH, RESOURCE_NOT_FOUND
    """
    # -------------------------------------------------------------------------
    # PATCH: BUGGY VERSION (uncomment to see failing tests)
    # -------------------------------------------------------------------------
    # BUG: Returns None instead of 404
    # The line `# return bookings_db.get(booking_id)` is a commented-out line of code in the
    # return bookings_db.get(booking_id)
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # PATCH: FIXED VERSION (current - tests pass)
    # -------------------------------------------------------------------------
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")
    return {"id": booking_id, **bookings_db[booking_id]}
    # -------------------------------------------------------------------------


@app.delete("/bookings/{booking_id}", tags=["Bookings"])
async def cancel_booking(booking_id: str):
    """
    Cancel a booking.

    **Intents**: HAPPY_PATH, RESOURCE_NOT_FOUND
    """
    # -------------------------------------------------------------------------
    # PATCH: BUGGY VERSION (uncomment to see failing tests)
    # -------------------------------------------------------------------------
    # BUG: Silently fails if booking doesn't exist
    # if booking_id in bookings_db:
    #     del bookings_db[booking_id]
    # return {"message": "Booking cancelled"}
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # PATCH: FIXED VERSION (current - tests pass)
    # -------------------------------------------------------------------------
    if booking_id not in bookings_db:
        raise HTTPException(status_code=404, detail=f"Booking {booking_id} not found")

    booking = bookings_db[booking_id]
    event_id = booking["event_id"]
    if event_id in events_db:
        events_db[event_id]["bookings"] -= booking["quantity"]

    del bookings_db[booking_id]
    return {"message": "Booking cancelled", "id": booking_id}
    # -------------------------------------------------------------------------


@app.get("/health", tags=["System"])
async def health():
    """Health check."""
    return {
        "status": "healthy",
        "events": len(events_db),
        "bookings": len(bookings_db),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8006)

"""
Fintech Transaction API - Full FastAPI Application

This API simulates a comprehensive fintech service for testing various validation intents.
It includes REST endpoints.

Intents Used by This API:
- HAPPY_PATH: Valid requests that should succeed
- REQUIRED_FIELD_MISSING: Missing required fields in requests
- TYPE_VIOLATION: Wrong data types (e.g., string instead of number)
- RESOURCE_NOT_FOUND: Invalid resource IDs (e.g., non-existent user or transfer)
- FORMAT_INVALID: Invalid formats (e.g., invalid email address)
- NUMBER_TOO_SMALL: Values below minimum (e.g., amount <= 0, account < 10000)
- NUMBER_TOO_LARGE: Values above maximum (e.g., amount > 10000, account > 99999)
- PATTERN_MISMATCH: Strings not matching required patterns (e.g., email regex)
- STRING_TOO_SHORT: Strings shorter than minimum length (e.g., name too short)
- STRING_TOO_LONG: Strings longer than maximum length (e.g., description too long)
- EMPTY_STRING: Empty string inputs where not allowed
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
import uvicorn
import asyncio
from datetime import datetime
from decimal import Decimal

app = FastAPI(
    title="Fintech Transaction API",
    description="A comprehensive sample API for testing Numeric Constraints, Realtime Features, and Security Intents.",
    version="2.0.0"
)

# In-memory storage for demo (replace with real DB in production)
users_db = {}
transfers_db = {}


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="User full name")
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", description="Valid email address")
    account_id: int = Field(..., ge=10000, le=99999, description="5-digit account ID")

class TransferRequest(BaseModel):
    amount: Decimal = Field(
        ...,
        gt=Decimal('0'),
        le=Decimal('10000.00'),
        multiple_of=Decimal('0.01'),
        description="Transfer amount in dollars (must include cents)"
    )
    from_account: int = Field(..., ge=10000, le=99999, description="Source account ID")
    to_account: int = Field(..., ge=10000, le=99999, description="Destination account ID")
    description: Optional[str] = Field(None, max_length=200, description="Optional transfer description")


class LimitUpdate(BaseModel):
    daily_limit: int = Field(..., ge=0, le=5000, description="Daily transaction limit")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="User risk score (0.0 to 1.0)")

class TransactionStatus(BaseModel):
    id: str
    status: str  # "pending", "processing", "completed", "failed"
    amount: Decimal
    from_account: int
    to_account: int
    timestamp: datetime


@app.post("/users", status_code=201, tags=["Users"])
async def create_user(user: UserCreate):
    """Create a new user account. Tests: REQUIRED_FIELD_MISSING, TYPE_VIOLATION, PATTERN_MISMATCH, BOUNDARY_MIN/MAX."""
    user_id = str(len(users_db) + 1)
    users_db[user_id] = user.dict()
    return {"id": user_id, **user.dict()}

@app.get("/users/{user_id}", tags=["Users"])
async def get_user(user_id: str):
    """Get user details. Tests: RESOURCE_NOT_FOUND."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **users_db[user_id]}

@app.post("/transfers/create", status_code=201, tags=["Transfers"])
async def create_transfer(transfer: TransferRequest):
    """
    Initiate a money transfer.
    Tests: REQUIRED_FIELD_MISSING, TYPE_VIOLATION, BOUNDARY_MIN/MAX, NOT_MULTIPLE_OF.
    """
    transfer_id = f"tx_{len(transfers_db) + 1}"
    
    # control empty string test
    if transfer.description == "":
        raise HTTPException(status_code=422, detail="Description cannot be an empty string")
    
    transfer_data = {
        "id": transfer_id,
        "status": "pending",
        "amount": transfer.amount,
        "from_account": transfer.from_account,
        "to_account": transfer.to_account,
        "description": transfer.description,
        "timestamp": datetime.now()
    }
    transfers_db[transfer_id] = transfer_data

    # Simulate processing
    asyncio.create_task(process_transfer(transfer_id))

    return {"id": transfer_id, "status": "pending", "amount": transfer.amount}

@app.get("/transfers/{transfer_id}", tags=["Transfers"])
async def get_transfer(transfer_id: str):
    """Get transfer status. Tests: RESOURCE_NOT_FOUND."""
    if transfer_id not in transfers_db:
        raise HTTPException(status_code=404, detail="Transfer not found")
    return transfers_db[transfer_id]

@app.post("/wallets/limit", status_code=200, tags=["Wallet"])
async def update_limit(limit: LimitUpdate):
    """
    Update wallet limits.
    Tests: REQUIRED_FIELD_MISSING, TYPE_VIOLATION, BOUNDARY_MIN/MAX.
    """
    return {"message": "Limit updated", "new_limit": limit.daily_limit, "risk_score": limit.risk_score}

# --- BACKGROUND TASKS ---
async def process_transfer(transfer_id: str):
    """Simulate transfer processing."""
    await asyncio.sleep(2)  # Simulate processing time

    transfer = transfers_db[transfer_id]
    transfer["status"] = "completed"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)

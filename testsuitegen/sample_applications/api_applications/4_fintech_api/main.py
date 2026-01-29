from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

app = FastAPI(
    title="Fintech Transaction API",
    description="A sample API for testing Numeric Constraints (Integer & Number).",
    version="1.0.0"
)

# --- 1. TRANSFERS (Numeric Boundaries & MultipleOf) ---

class TransferRequest(BaseModel):
    amount: float = Field(
        ..., 
        gt=0, 
        le=10000.00, 
        multiple_of=0.01,
        description="Transfer amount. Tests min/max boundaries and decimal precision."
    )
    from_account: int = Field(
        ..., 
        ge=10000, 
        le=99999, 
        description="Source account ID (5 digits)"
    )
    to_account: int = Field(
        ..., 
        ge=10000, 
        le=99999, 
        description="Destination account ID (5 digits)"
    )

@app.post("/transfers/create", status_code=201, tags=["Transfers"])
async def create_transfer(transfer: TransferRequest):
    """
    Initiate a money transfer.
    Tests:
    - BOUNDARY_MIN_MINUS_ONE (amount, accounts)
    - BOUNDARY_MAX_PLUS_ONE (amount, accounts)
    - NOT_MULTIPLE_OF (amount)
    - TYPE_VIOLATION (amount - strings)
    """
    return {"status": "Processing", "amount": transfer.amount}


# --- 2. WALLET LIMITS (Integer Boundaries & Zero) ---

class LimitUpdate(BaseModel):
    daily_limit: int = Field(
        ..., 
        ge=0, 
        le=5000, 
        description="Daily transaction limit."
    )
    risk_score: float = Field(
        ..., 
        ge=0.0, 
        le=1.0, 
        description="User risk score (0.0 to 1.0)"
    )

@app.post("/wallets/limit", status_code=200, tags=["Wallet"])
async def update_limit(limit: LimitUpdate):
    """
    Update wallet limits.
    Tests:
    - BOUNDARY_MIN_MINUS_ONE (daily_limit < 0, risk_score < 0.0)
    - BOUNDARY_MAX_PLUS_ONE (daily_limit > 5000, risk_score > 1.0)
    - TYPE_VIOLATION (daily_limit - float/string)
    """
    return {"message": "Limit updated", "new_limit": limit.daily_limit}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)

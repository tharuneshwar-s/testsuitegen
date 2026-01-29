from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Set, Optional, Dict, Any
import uvicorn

app = FastAPI(
    title="Warehouse Inventory API",
    description="A sample API for testing Array & Object Constraints (Nested Structures).",
    version="1.0.0"
)

# --- 1. ARRAYS & NESTED OBJECTS (Bulk Shipments) ---

class Item(BaseModel):
    sku: str = Field(..., min_length=5, max_length=20)
    qty: int = Field(..., ge=1)

class Shipment(BaseModel):
    shipment_id: str
    items: List[Item] = Field(
        ..., 
        min_items=1, 
        max_items=50, 
        description="List of items in shipment"
    )
    tags: Set[str] = Field(
        ..., 
        min_items=1, 
        max_items=5, 
        description="Unique tags for shipment"
    )

@app.post("/shipments/bulk", status_code=201, tags=["Shipments"])
async def create_shipment(shipment: Shipment):
    """
    Create a bulk shipment.
    Tests:
    - BOUNDARY_MIN/MAX_ITEMS (items, tags)
    - ARRAY_NOT_UNIQUE (tags - passing duplicates)
    - ARRAY_ITEM_TYPE_VIOLATION (items - passing strings instead of objects)
    """
    return {"message": "Shipment received", "count": len(shipment.items)}


# --- 2. OBJECT CONSTRAINTS (Product Specs) ---

class TechnicalSpecs(BaseModel):
    model_config = ConfigDict(extra='forbid')  # additionalProperties: false
    
    voltage: int
    amperage: float
    dimensions: Dict[str, float]

class Product(BaseModel):
    name: str
    specs: TechnicalSpecs

@app.post("/products/specs", status_code=201, tags=["Products"])
async def create_product(product: Product):
    """
    Register product specifications.
    Tests:
    - ADDITIONAL_PROPERTY_NOT_ALLOWED (specs - sending extra fields)
    - REQUIRED_FIELD_MISSING (voltage, amperage)
    - OBJECT_VALUE_TYPE_VIOLATION (dimensions - sending list instead of dict)
    """
    return {"message": "Product registered", "name": product.name}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8005)

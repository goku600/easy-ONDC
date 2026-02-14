from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# --- Requests ---
class VendorOnboardRequest(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    category: Optional[str] = None
    contact: Optional[str] = None
    structured_data: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None  # For OCR or messy input

class VendorSearchRequest(BaseModel):
    query: str
    limit: int = 3

# --- Responses ---
class VendorResponse(BaseModel):
    id: str
    name: str
    location: str
    category: str
    contact: str
    score: float

class SearchResponse(BaseModel):
    ai_summary: str
    vendors: List[VendorResponse]

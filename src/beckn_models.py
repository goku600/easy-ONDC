from pydantic import BaseModel, Field
from typing import List, Optional, Any
from datetime import datetime

# --- ONDC / Beckn Core Models ---

class Context(BaseModel):
    domain: str = "ONDC:RET10"  # Retail Domain
    country: str = "IND"
    city: str
    action: str  # search, on_search, select, on_select, etc.
    core_version: str = "1.2.0"
    bap_id: str  # Buyer App ID
    bap_uri: str # Buyer App URI
    bpp_id: Optional[str] = None # Seller App ID (Us)
    bpp_uri: Optional[str] = None # Seller App URI (Us)
    transaction_id: str
    message_id: str
    timestamp: datetime
    ttl: str = "PT30S"

class Descriptor(BaseModel):
    name: str
    code: Optional[str] = None
    symbol: Optional[str] = None
    short_desc: Optional[str] = None
    long_desc: Optional[str] = None
    images: Optional[List[str]] = None

class Item(BaseModel):
    id: str
    descriptor: Descriptor
    price: Optional[Any] = None
    category_id: Optional[str] = None
    fulfillment_id: Optional[str] = None

class Provider(BaseModel):
    id: str
    descriptor: Descriptor
    items: List[Item]
    locations: Optional[List[Any]] = None

class Catalog(BaseModel):
    descriptor: Descriptor
    providers: List[Provider]

class Intent(BaseModel):
    item: Optional[dict] = None
    provider: Optional[dict] = None
    fulfillment: Optional[dict] = None
    category: Optional[dict] = None
    tags: Optional[List[dict]] = None

class SearchMessage(BaseModel):
    intent: Intent

class OnSearchMessage(BaseModel):
    catalog: Catalog

# --- API Request/Response Wrappers ---

class BecknSearchRequest(BaseModel):
    context: Context
    message: SearchMessage

class BecknOnSearchRequest(BaseModel):
    context: Context
    message: OnSearchMessage

class BecknAck(BaseModel):
    message: dict = {"ack": {"status": "ACK"}}
    error: Optional[dict] = None

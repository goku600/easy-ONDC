from src.beckn_models import (
    BecknSearchRequest, BecknOnSearchRequest, Context, Catalog, Provider, Item, Descriptor, OnSearchMessage
)
from src.services.vendor_service import VendorService
from src.models import VendorSearchRequest
from src.config import get_settings
import requests
import datetime

settings = get_settings()

class BecknService:
    def __init__(self):
        self.vendor_service = VendorService()
        self.bpp_id = "ondc-setu-node"
        self.bpp_uri = "http://localhost:8000/v1/beckn" # Placeholder

    def process_search(self, request: BecknSearchRequest):
        """
        Processes an incoming ONDC /search request.
        Since ONDC is async, this function should ideally be run in a background task (Celery/FastAPI BackgroundTasks).
        """
        # 1. Extract query from Intent
        query = ""
        if request.message.intent.item and request.message.intent.item.get("descriptor"):
             query = request.message.intent.item["descriptor"].get("name", "")
        elif request.message.intent.category:
             query = request.message.intent.category.get("descriptor", {}).get("id", "")
        
        if not query:
            query = "general search" # Fallback

        print(f"DEBUG: Processing ONDC Search for '{query}'")

        # 2. Use our existing Intelligent Agent
        # We perform a semantic search using the extracted intent
        internal_results = self.vendor_service.search_vendors(VendorSearchRequest(query=query, limit=5))

        # 3. Transform to ONDC Catalog format
        providers = []
        for v in internal_results.vendors:
            # For this demo, we assume each vendor sells 1 generic item matching the query
            # In a real system, you'd fetch the vendor's actual catalog
            item = Item(
                id=f"item-{v.id}",
                descriptor=Descriptor(
                    name=f"Service/Product by {v.name}",
                    short_desc=v.category,
                    long_desc=f"{v.category} provided by {v.name} in {v.location}"
                )
            )
            
            provider = Provider(
                id=v.id,
                descriptor=Descriptor(
                    name=v.name,
                    short_desc=v.location
                ),
                items=[item]
            )
            providers.append(provider)

        catalog = Catalog(
            descriptor=Descriptor(name="ONDC Setu Catalog"),
            providers=providers
        )

        # 4. Construct /on_search body
        on_search_body = BecknOnSearchRequest(
            context=self._create_reply_context(request.context, action="on_search"),
            message=OnSearchMessage(catalog=catalog)
        )

        # 5. Send Callback (Web Hook) to the BAP (Buyer App)
        # Note: In a real deployment, BAP_URI would be a public URL
        print(f"DEBUG: Sending /on_search to {request.context.bap_uri}")
        
        # In a real scenario, we would do:
        # requests.post(f"{request.context.bap_uri}/on_search", json=on_search_body.dict())
        
        return on_search_body # Returning for demo/testing purposes

    def _create_reply_context(self, req_context: Context, action: str) -> Context:
        new_context = req_context.copy()
        new_context.action = action
        new_context.bpp_id = self.bpp_id
        new_context.bpp_uri = self.bpp_uri
        new_context.timestamp = datetime.datetime.now()
        return new_context

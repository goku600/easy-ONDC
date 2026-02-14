import uuid
from src.models import VendorOnboardRequest, VendorSearchRequest, SearchResponse, VendorResponse
from src.dependencies import get_collection, get_llm_client
from src.config import get_settings

class VendorService:
    def __init__(self):
        self.collection = get_collection()
        self.client = get_llm_client()
        self.settings = get_settings()

    def onboard_vendor(self, data: VendorOnboardRequest):
        # 1. Prepare Text for Embedding
        text_to_embed = ""
        if data.raw_text:
            text_to_embed = f"Raw Content: {data.raw_text}"
        else:
            s_data = data.structured_data or {}
            text_to_embed = f"Vendor: {data.name}. Location: {data.location}. Category: {data.category}. Details: {s_data}"

        # 2. Prepare Metadata
        metadata = {
            "id": str(uuid.uuid4()),
            "name": data.name or "Unknown",
            "location": data.location or "Unknown",
            "category": data.category or "Unknown",
            "contact": data.contact or "Unknown"
        }

        # 3. Add to Chroma
        self.collection.add(
            documents=[text_to_embed],
            metadatas=[metadata],
            ids=[metadata["id"]]
        )
        return {"status": "success", "id": metadata["id"]}

    def search_vendors(self, request: VendorSearchRequest) -> SearchResponse:
        # 1. Query Chroma
        results = self.collection.query(
            query_texts=[request.query],
            n_results=request.limit
        )

        if not results['documents'] or not results['documents'][0]:
            return SearchResponse(ai_summary="No matching vendors found.", vendors=[])

        # 2. Process Results
        vendors = []
        context_text = ""
        
        for i in range(len(results['documents'][0])):
            doc = results['documents'][0][i]
            meta = results['metadatas'][0][i]
            dist = results['distances'][0][i] if 'distances' in results and results['distances'] else 0.0
            
            v = VendorResponse(
                id=meta.get("id"),
                name=meta.get("name"),
                location=meta.get("location"),
                category=meta.get("category"),
                contact=meta.get("contact"),
                score=dist
            )
            vendors.append(v)
            context_text += f"Vendor {i+1}: {doc}\nMetadata: {meta}\n\n"

        # 3. Generate AI Summary using google-genai SDK
        prompt = f"""You are an intelligent procurement assistant for ONDC. Recommend vendors based on the provided context.
        
User Query: {request.query}

Vendor Context:
{context_text}
"""
        response = self.client.models.generate_content(
            model=self.settings.GEMINI_MODEL_NAME,
            contents=prompt
        )
        
        return SearchResponse(
            ai_summary=response.text,
            vendors=vendors
        )

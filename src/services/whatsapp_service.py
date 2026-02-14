import json
from src.dependencies import get_llm_client
from src.config import get_settings
from src.models import VendorOnboardRequest
from src.services.vendor_service import VendorService

settings = get_settings()

class WhatsAppService:
    def __init__(self):
        self.client = get_llm_client()
        self.vendor_service = VendorService()

    def parse_vendor_message(self, message: str, sender: str) -> dict:
        """
        Uses Gemini AI to extract structured vendor information
        from a raw WhatsApp message.
        """
        prompt = f"""You are an ONDC vendor onboarding assistant. 
A vendor just sent this WhatsApp message to register their business:

"{message}"

Extract the following fields from the message. If a field is not found, use "Unknown".
Return ONLY a valid JSON object with these exact keys:
{{
  "name": "business name",
  "location": "city or area",
  "category": "product/service category",
  "contact": "{sender}"
}}

Return ONLY the JSON, no other text."""

        response = self.client.models.generate_content(
            model=settings.GEMINI_MODEL_NAME,
            contents=prompt
        )
        
        # Parse AI response into dict
        try:
            # Clean the response (remove markdown code blocks if present)
            text = response.text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1]  # Remove first line
                text = text.rsplit("```", 1)[0]  # Remove last ```
            return json.loads(text)
        except (json.JSONDecodeError, Exception) as e:
            print(f"AI parsing failed: {e}, raw: {response.text}")
            return {
                "name": "Unknown",
                "location": "Unknown", 
                "category": "Unknown",
                "contact": sender
            }

    def classify_intent(self, message: str) -> str:
        """
        Uses Gemini AI to classify the user's intent.
        Returns: "onboard", "search", or "unknown"
        """
        prompt = f"""You are an ONDC assistant. A user sent this message via WhatsApp:

"{message}"

Classify the intent into one of these categories:
1. "onboard" -> If the user wants to register, join, or list their business/products.
2. "search" -> If the user is looking for a product, service, or vendor.
3. "unknown" -> If the intent is unclear.

Return ONLY the category name (onboard, search, or unknown). 
Do NOT return "Category: search" or any punctuation. Just the word."""

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=prompt
            )
            raw_intent = response.text.strip().lower()
            print(f"DEBUG: Message: '{message}' -> Classified Intent: '{raw_intent}'")
            
            # Basic cleanup
            intent = raw_intent.replace('"', '').replace("'", "").rstrip('.')
            
            if intent not in ["onboard", "search", "unknown"]:
                return "unknown"
            return intent
        except Exception as e:
            print(f"Intent classification failed: {e}")
            return "unknown"

    def perform_search(self, message: str) -> str:
        """
        Handles search intent.
        """
        # For simplicity, we use the message itself as the query.
        # In a more advanced version, we could use AI to extract the core query.
        from src.models import VendorSearchRequest # delayed import to avoid circular dependency if any

        try:
            # Create a search request
            request = VendorSearchRequest(query=message, limit=3)
            search_response = self.vendor_service.search_vendors(request)
            
            if not search_response.vendors:
                return f"I couldn't find any vendors matching '{message}'. Try a different search."

            # Format the response
            reply = [f"Here are some vendors for '{message}':\n"]
            for v in search_response.vendors:
                reply.append(f"* {v.name} ({v.category})\n  Loc: {v.location}\n  Contact: {v.contact}\n")
            
            reply.append("\nReply with a message to search again or register your own business!")
            return "\n".join(reply)

        except Exception as e:
            print(f"Search failed: {e}")
            return "Sorry, I encountered an error while searching."

    def handle_incoming_message(self, message: str, sender: str) -> str:
        """
        Main handler for incoming WhatsApp messages.
        1. Classifies intent.
        2. Routes to appropriate handler.
        """
        intent = self.classify_intent(message)
        
        if intent == "onboard":
            return self._handle_onboarding(message, sender)
        elif intent == "search":
            return self.perform_search(message)
        else:
            return (
                "Welcome to ONDC! I didn't quite understand that.\n\n"
                "- To register your business, describe your shop (e.g., 'Register my grocery store in Indiranagar').\n"
                "- To find vendors, just ask (e.g., 'Find plumbers nearby')."
            )

    def _handle_onboarding(self, message: str, sender: str) -> str:
        """
        Existing onboarding logic, moved to a private method.
        """
        # 1. Use AI to extract vendor info
        parsed = self.parse_vendor_message(message, sender)
        
        # 2. Create onboard request
        request = VendorOnboardRequest(
            name=parsed.get("name", "Unknown"),
            location=parsed.get("location", "Unknown"),
            category=parsed.get("category", "Unknown"),
            contact=parsed.get("contact", sender),
            raw_text=message
        )
        
        # 3. Onboard
        result = self.vendor_service.onboard_vendor(request)
        
        # 4. Build reply
        if result.get("status") == "success":
            reply = (
                f"Welcome to ONDC! Your business has been registered.\n\n"
                f"Name: {parsed.get('name')}\n"
                f"Location: {parsed.get('location')}\n"
                f"Category: {parsed.get('category')}\n"
                f"ID: {result.get('id')}\n\n"
                f"Buyers can now discover you on the ONDC network!"
            )
        else:
            reply = "Sorry, we could not process your registration. Please try again."
        
        return reply

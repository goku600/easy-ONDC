import json
import requests
from src.dependencies import get_llm_client
from src.config import get_settings
from src.models import VendorOnboardRequest
from src.services.vendor_service import VendorService

settings = get_settings()

class TelegramService:
    def __init__(self):
        self.client = get_llm_client()
        self.vendor_service = VendorService()
        self.base_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"

    def send_message(self, chat_id: int, text: str):
        """
        Sends a message to a Telegram chat.
        """
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}
        try:
            requests.post(url, json=payload)
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

    def parse_vendor_message(self, message: str, sender: str) -> dict:
        """
        Uses Gemini AI to extract structured vendor information.
        Reused from WhatsAppService logic.
        """
        prompt = f"""You are an ONDC vendor onboarding assistant. 
A vendor just sent this message to register their business:

"{message}"

Extract the following fields. If a field is not found, use "Unknown".
Return ONLY a valid JSON object (no markdown) with these exact keys:
{{
  "name": "business name",
  "location": "city or area",
  "category": "product/service category",
  "contact": "{sender}"
}}"""

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=prompt
            )
            text = response.text.strip()
            # Clean markdown if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0]
            return json.loads(text)
        except Exception as e:
            print(f"AI parsing failed: {e}")
            return {
                "name": "Unknown",
                "location": "Unknown", 
                "category": "Unknown",
                "contact": sender
            }

    def classify_intent(self, message: str) -> str:
        """
        Uses Gemini AI to classify intent.
        """
        prompt = f"""You are an ONDC assistant. A user sent this message:

"{message}"

Classify the intent into one of these categories:
1. "onboard" -> Register/join/list business.
2. "search" -> Looking for product/service/vendor.
3. "unknown" -> Unclear.

Return ONLY the category name (onboard, search, or unknown). 
Do NOT return "Category: search" or any punctuation. Just the word."""

        try:
            response = self.client.models.generate_content(
                model=settings.GEMINI_MODEL_NAME,
                contents=prompt
            )
            raw = response.text.strip().lower()
            # Cleanup
            intent = raw.replace('"', '').replace("'", "").rstrip('.')
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
        from src.models import VendorSearchRequest
        try:
            request = VendorSearchRequest(query=message, limit=3)
            search_response = self.vendor_service.search_vendors(request)
            
            if not search_response.vendors:
                return f"I couldn't find any vendors matching '{message}'."

            reply = [f"Here are some vendors for '{message}':\n"]
            for v in search_response.vendors:
                reply.append(f"• {v.name} ({v.category})\n  📍 {v.location}\n  📞 {v.contact}\n")
            
            reply.append("\nReply to search again or register your business!")
            return "\n".join(reply)
        except Exception as e:
            print(f"Search failed: {e}")
            return "Sorry, I encountered an error while searching."

    def handle_incoming_update(self, update: dict):
        """
        Main handler for Telegram Webhook updates.
        """
        try:
            message_data = update.get("message", {})
            if not message_data:
                return # Not a text message or unsupported update
            
            chat_id = message_data.get("chat", {}).get("id")
            text = message_data.get("text", "")
            user_first_name = message_data.get("from", {}).get("first_name", "User")
            
            if not text or not chat_id:
                return

            print(f"Telegram Message from {user_first_name}: {text}")

            # 1. Classify
            intent = self.classify_intent(text)
            print(f"Classified Intent: {intent}")

            # 2. Route
            if intent == "onboard":
                reply = self._handle_onboarding(text, str(chat_id))
            elif intent == "search":
                reply = self.perform_search(text)
            else:
                reply = (
                    f"Hi {user_first_name}! Welcome to ONDC.\n\n"
                    "• *Register*: 'Register my bakery in Delhi'\n"
                    "• *Search*: 'Find electricians nearby'"
                )

            # 3. Send Reply
            self.send_message(chat_id, reply)

        except Exception as e:
            print(f"Error handling Telegram update: {e}")

    def _handle_onboarding(self, message: str, sender_id: str) -> str:
        parsed = self.parse_vendor_message(message, sender_id)
        
        request = VendorOnboardRequest(
            name=parsed.get("name", "Unknown"),
            location=parsed.get("location", "Unknown"),
            category=parsed.get("category", "Unknown"),
            contact=parsed.get("contact", sender_id), # Using chat_id/sender as contact for now
            raw_text=message
        )
        
        result = self.vendor_service.onboard_vendor(request)
        
        if result.get("status") == "success":
            return (
                f"✅ Business Registered!\n\n"
                f"Name: {parsed.get('name')}\n"
                f"Location: {parsed.get('location')}\n"
                f"Category: {parsed.get('category')}\n"
                f"ID: {result.get('id')}\n\n"
                f"You are now discoverable on ONDC."
            )
        else:
            return "❌ Registration failed. Please try again."

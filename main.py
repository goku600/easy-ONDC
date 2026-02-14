from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Form
from fastapi.responses import PlainTextResponse
from src.models import VendorOnboardRequest, VendorSearchRequest, SearchResponse
from src.beckn_models import BecknSearchRequest, BecknAck
from src.services.vendor_service import VendorService
from src.services.beckn_service import BecknService
from src.services.whatsapp_service import WhatsAppService
from src.security import verify_admin_key
from src.dependencies import get_chroma_client
from twilio.twiml.messaging_response import MessagingResponse
import uvicorn
import os

app = FastAPI(
    title="ONDC-Setu API",
    description="Intelligent ONDC Node for Vendor Digitization & Search",
    version="1.0.0"
)

# Dependency to get service
def get_service():
    return VendorService()

# Dependency for Beckn Service
def get_beckn_service():
    return BecknService()

def get_whatsapp_service():
    return WhatsAppService()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "ONDC-Setu API", "beckn_ready": True}

@app.post("/v1/beckn/search", response_model=BecknAck)
def beckn_search(request: BecknSearchRequest, background_tasks: BackgroundTasks, service: BecknService = Depends(get_beckn_service)):
    """
    ONDC /search endpoint.
    1. Returns ACK immediately.
    2. Triggers background processing to find vendors.
    3. Calls listener's /on_search later.
    """
    try:
        # Simulate async processing
        background_tasks.add_task(service.process_search, request)
        return BecknAck()
    except Exception as e:
        print(f"Error processing Beckn request: {e}")
        return BecknAck(error={"type": "DOMAIN-ERROR", "message": str(e)})

@app.post("/v1/vendor/onboard", dependencies=[Depends(verify_admin_key)])
def onboard_vendor(request: VendorOnboardRequest, service: VendorService = Depends(get_service)):
    try:
        result = service.onboard_vendor(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/search", response_model=SearchResponse)
def search_vendors(request: VendorSearchRequest, service: VendorService = Depends(get_service)):
    try:
        result = service.search_vendors(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---- WhatsApp Integration ----

@app.post("/v1/whatsapp/webhook")
def whatsapp_webhook(
    Body: str = Form(...),
    From: str = Form(...),
    service: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Twilio WhatsApp Webhook.
    Receives incoming messages and auto-onboards vendors.
    """
    try:
        reply_text = service.handle_incoming_message(message=Body, sender=From)
        # Build TwiML response
        twiml = MessagingResponse()
        twiml.message(reply_text)
        return PlainTextResponse(content=str(twiml), media_type="application/xml")
    except Exception as e:
        print(f"WhatsApp webhook error: {e}")
        twiml = MessagingResponse()
        twiml.message("Sorry, something went wrong. Please try again.")
        return PlainTextResponse(content=str(twiml), media_type="application/xml")

@app.post("/v1/whatsapp/test")
def test_whatsapp(message: str, sender: str = "test-user", service: WhatsAppService = Depends(get_whatsapp_service)):
    """
    Test endpoint to simulate WhatsApp onboarding WITHOUT Twilio.
    Use this in Swagger UI or curl for demos.
    """
    reply = service.handle_incoming_message(message=message, sender=sender)
    return {"reply": reply}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

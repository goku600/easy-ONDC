from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from src.config import get_settings
import os

# Define the header key
API_KEY_HEADER = APIKeyHeader(name="X-Admin-Key", auto_error=False)

def get_admin_key():
    # In production, this should be a strong secret set in environment variables
    # Defaulting to a placeholder if not set, but warning the user
    key = os.getenv("ADMIN_API_KEY", "secret-admin-key-123")
    return key

async def verify_admin_key(api_key: str = Security(API_KEY_HEADER)):
    """
    Verifies the Admin API Key for protected endpoints (like Onboarding).
    """
    correct_key = get_admin_key()
    
    if api_key == correct_key:
        return api_key
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid or missing Admin API Key"
    )

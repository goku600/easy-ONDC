from functools import lru_cache
import chromadb
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from google import genai
from google.genai import types
from src.config import get_settings
import os

settings = get_settings()

# Custom Embedding Function for ChromaDB using new google-genai SDK
class GoogleGenAIEmbeddingFunction(EmbeddingFunction):
    def __init__(self, api_key: str, model_name: str):
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def __call__(self, input: Documents) -> Embeddings:
        try:
            response = self.client.models.embed_content(
                model=self.model_name,
                contents=input
            )
            if response.embeddings:
                 return [e.values for e in response.embeddings]
            return []
        except Exception as e:
            print(f"ERROR: Embedding failed: {e}")
            return []

@lru_cache()
def get_chroma_client():
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
    return chromadb.PersistentClient(path=settings.CHROMA_DB_DIR)

@lru_cache()
def get_embedding_function():
    return GoogleGenAIEmbeddingFunction(
        api_key=settings.GOOGLE_API_KEY,
        model_name=settings.EMBEDDING_MODEL_NAME
    )

@lru_cache()
def get_llm_client():
    """Returns the raw Google GenAI Client"""
    return genai.Client(api_key=settings.GOOGLE_API_KEY)

def get_collection():
    client = get_chroma_client()
    ef = get_embedding_function()
    return client.get_or_create_collection(name="vendor_profiles", embedding_function=ef)

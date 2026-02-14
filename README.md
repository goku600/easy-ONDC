# ONDC-Setu Production API

A scalable, containerized FastAPI backend for the ONDC Vendor Digitization & Intelligence node.

## 🚀 Features
- **Vendor Onboarding**: Ingest structured profile data or raw text/OCR.
- **Intelligent Search**: Concept-based (semantic) search using Google Gemini Embeddings & ChromaDB.
- **Production Ready**: Async generic API, Dockerized, Type-safe (Pydantic).

## 🛠️ Setup

### Prerequisites
- Python 3.9+
- Google Gemini API Key

### Installation
1.  **Create Virtual Environment**:
    ```bash
    python -m venv .venv
    # Windows
    .\.venv\Scripts\Activate
    # Mac/Linux
    source .venv/bin/activate
    ```
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure Environment**:
    - Update `GOOGLE_API_KEY` in `.env` file.

## 🏃 Run Locally
Start the server with `uvicorn` (auto-reload enabled):
```bash
uvicorn main:app --reload
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health Check: [http://localhost:8000/](http://localhost:8000/)

## 🐳 Run with Docker
Ship anywhere with Docker Compose:
```bash
docker-compose up --build
```
The API will be available at `http://localhost:8000`.

## 📡 API Endpoints

### `POST /v1/vendor/onboard`
Submit vendor details to the vector database.
```json
{
  "name": "Eco Bamboo Crafts",
  "location": "Assam, India",
  "category": "Home Decor",
  "structured_data": {"material": "Bamboo", "type": "Handmade"}
}
```

### `POST /v1/search`
Search for vendors using natural language.
```json
{
  "query": "sustainable home decor items from northeast india"
}
```

# 🚀 ONDC-Setu GenAI Node (Telegram Edition)

A production-ready **ONDC Network Node** powered by **Google Gemini AI** and **Vector Search**. This system allows vendors to onboard and be discovered using natural language through a **Telegram Bot**.

Built with: **FastAPI** (Backend), **ChromaDB** (Vector Database), **Google Gemini** (AI/LLM), and **Telegram Bot API**.

---

## 🌟 Features
*   **🤖 AI-Powered Onboarding**: Vendors serve their details via chat (e.g., *"Register my bakery in Indiranagar"*). The AI extracts structured data automatically.
*   **🧠 Semantic Search**: Users find products by *concept*, not just keywords (e.g., *"Find me gluten-free snacks"* matches a bakery).
*   **💬 Telegram Integration**: Replaces complex/paid WhatsApp APIs with a free, scalable Telegram Bot.
*   **☁️ Cloud Ready**: One-click deployment to **Render** (Free Tier compatible).
*   **🔗 ONDC Protocol**: Implements `beckn` protocol standards for decentralized commerce.

---

## 🛠️ Prerequisites
Before checking out the code, ensure you have:
1.  **Google Gemini API Key**: [Get it here (Free)](https://aistudio.google.com/app/apikey)
2.  **Telegram Bot Token**: Message `@BotFather` on Telegram to create a new bot and get the token.
3.  **Render Account**: [Sign up here](https://render.com/) for deployment.

---

## 💻 Local Setup (For Developers)

### 1. Clone & Install
```bash
git clone https://github.com/your-username/easy-ONDC.git
cd easy-ONDC

# Create Virtual Environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate

# Install Dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)
Create a file named `.env` in the root folder:
```ini
PYTHON_VERSION=3.11.0
GOOGLE_API_KEY=your_gemini_key_here
TELEGRAM_BOT_TOKEN=your_telegram_token_here
CHROMA_DB_DIR=data/chroma
```

### 3. Run Locally
```bash
uvicorn main:app --reload
```
*   Server runs at: `http://localhost:8000`
*   Swagger Docs: `http://localhost:8000/docs`

---

## 🚀 Deployment Guide (Zero to Hero)

We use **Render** for free cloud hosting.

### Step 1: Push to GitHub
If you haven't already:
```bash
git init
git add .
git commit -m "Initial commit"
# Create a repo on GitHub and follow the instructions to push
git branch -M main
git remote add origin https://github.com/YOUR_USER/YOUR_REPO.git
git push -u origin main
```

### Step 2: Create Web Service on Render
1.  Go to **Render Dashboard** > **New +** > **Web Service**.
2.  Connect your GitHub repository.
3.  **Settings**:
    *   **Runtime**: Python 3
    *   **Build Command**: `pip install -r requirements.txt`
    *   **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`
4.  **Environment Variables** (Critical!):
    *   `PYTHON_VERSION`: `3.11.0`
    *   `GOOGLE_API_KEY`: *[Paste your Gemini Key]*
    *   `TELEGRAM_BOT_TOKEN`: *[Paste your Telegram Token]*
5.  Click **Create Web Service**.

### Step 3: Connect Telegram Webhook
Once Render says **"Live"**, you need to tell Telegram where your server is.
Run this script locally (replace with your Render URL):

```bash
# Example: https://ondc-setu-api.onrender.com
python set_webhook.py <YOUR_RENDER_URL>
```

*Success Message:* `{'ok': True, 'result': True, 'description': 'Webhook was set'}`

---

## 📱 How to Use
Open your bot in Telegram and chat naturally!

### Vendor Registration
> **User**: "Register my electronics shop 'Super Gadgets' in Bangalore. We sell laptops and phones."
>
> **Bot**: "✅ Business Registered! You are now discoverable on ONDC."

### Product Search
> **User**: "I need a fast laptop for gaming."
>
> **Bot**: "Here are some vendors for 'fast laptop':
> • Super Gadgets (Electronics) - Bangalore"

---

## 📁 Project Structure
*   `src/services/telegram_service.py`: Handles Bot logic & AI intent classification.
*   `src/services/vendor_service.py`: Manages Vector Database (ChromaDB) operations.
*   `src/services/whatsapp_service.py`: (Legacy) Old WhatsApp logic.
*   `main.py`: The API Gateway handling webhooks.
*   `test_api.py`: Verification script for testing endpoints.

---

## ⚠️ Notes for Free Tier
On Render's Free Tier, the **database resets** every time the server restarts (ephemeral storage). For persistent data, upgrade to a Paid Plan with a "Render Disk" or use an external database like MongoDB/PostgreSQL.

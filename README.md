# 🔍 CrisisLens

> **A government-grade real-time misinformation response platform built with AI.**

CrisisLens is an intelligent operations dashboard and citizen portal designed to rapidly verify crisis claims, monitor active hotspots, and ingest live social/news signals to prevent panic and guide official responses.

---

## 🌟 Key Features

- **🛡️ Authority Command Center:** A real-time intelligence dashboard tracking priority incidents, fake claims, and risk hotspots.
- **🗺️ Interactive Heatmaps:** Live OpenStreetMap integration visualizing crisis density using PyDeck.
- **🧠 LangGraph Pipeline:** Multi-agent verification pipeline orchestrating extraction, risk analysis, and action recommendations.
- **🌐 Global Live Signals:** Dynamically fetches live crisis events from the GNews API.
- **📝 Citizen Verification Portal:** Allows the public to verify suspicious text claims or upload screenshots via OCR (Tesseract/OpenCV).
- **🤖 Gemini AI Integration:** Leverages Google Gemini to generate human-readable explanations and public safety actions.

---

## 🏛️ Architecture

- **Frontend:** Streamlit
- **Database:** SQLite (managed via `sqlite-utils`)
- **Mapping:** PyDeck + Geopy (Nominatim caching)
- **AI/LLM:** LangGraph, LangChain, Google Generative AI
- **Integrations:** GNews API, Tesseract OCR

---

## ⚙️ Setup & Installation

**1. Clone the repository and setup your environment:**
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Configure Environment Variables:**
Copy `.env.example` to `.env` and fill in your keys:
```env
GNEWS_API_KEY=your_gnews_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If keys are missing, the app gracefully falls back to mock data streams, guaranteeing stability during presentations!)*

**4. Run the Platform:**
```bash
streamlit run app.py
```

---

## 🔐 Demo Credentials
- **Authority/Admin:** `admin` / `admin123`
- **Citizen:** `user` / `user123`

---
*Built with ❤️ for Crisis Response & Misinformation Mitigation.*

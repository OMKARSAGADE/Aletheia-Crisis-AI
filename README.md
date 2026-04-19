# Aletheia -- Real-Time Crisis Intelligence Platform

Aletheia is a multi-agent AI framework for real-time crisis claim verification, risk assessment, and geospatial intelligence. Built for authorities and citizens to combat misinformation during emergencies.

---

## Features

- **Multi-Agent Pipeline** -- 5 specialized AI agents orchestrated via LangGraph
- **Dual Dashboards** -- Separate interfaces for Citizens (submit and verify) and Authorities (monitor and act)
- **Live Crisis Feeds** -- Real-time global alerts via GNews API
- **AI-Powered Verification** -- Gemini LLM analyzes claims for credibility and risk
- **OCR Support** -- Extract and verify text from screenshots of suspicious messages
- **Geospatial Mapping** -- Interactive crisis heatmaps with location-based filtering
- **Analytics Dashboard** -- Risk distribution, verdict breakdown, and hotspot charts
- **Scenario Simulator** -- Inject test crisis scenarios (Flood, Fire, Collapse) for demos
- **Agent Observability** -- Full execution tracing via Langfuse integration
- **Role-Based Auth** -- Secure login routing for Citizens and Authorities

---

## Architecture

```
User Input (Text / Image via OCR)
        |
        v
+------------------------------------------+
|           LangGraph Orchestrator         |
|                                          |
|  +------------+    +-----------------+   |
|  | Extraction |--->|  Verification   |   |
|  |   Agent    |    |     Agent       |   |
|  +------------+    +--------+--------+   |
|                             |            |
|                             v            |
|                     +------------+       |
|                     | Risk Agent |       |
|                     +------+-----+       |
|                            |             |
|                            v             |
|                     +--------------+     |
|                     | Action Agent |     |
|                     +------+-------+     |
|                            |             |
|                            v             |
|                     +---------------+    |
|                     | Summary Agent |    |
|                     +---------------+    |
|                                          |
|         Langfuse Tracing (all nodes)     |
+------------------------------------------+
        |
        v
  Dashboard + DB + Maps + Charts
```

### Agents

| Agent | Role |
|---|---|
| **Extraction Agent** | Parses claims, extracts location, entities, and crisis type |
| **Verification Agent** | Cross-references with GNews and Gemini for credibility scoring |
| **Risk Agent** | Assigns risk score based on severity, location, and patterns |
| **Action Agent** | Recommends response actions for authorities |
| **Summary Agent** | Generates a final structured intelligence report |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Agent Framework | LangGraph + LangChain |
| LLM | Google Gemini API |
| News Intelligence | GNews API |
| OCR | Tesseract (pytesseract) |
| Database | SQLite |
| Maps | PyDeck |
| Charts | Plotly |
| Geocoding | GeoPy |
| Observability | Langfuse |
| Auth | Session-based (bcrypt) |

---

## Project Structure

```
crisislens/
|-- app.py                    # Main entry point
|-- requirements.txt          # Python dependencies
|-- .env.example              # Environment variable template
|-- .gitignore
|
|-- agents/                   # LangGraph multi-agent pipeline
|   |-- graph.py              # LangGraph DAG definition
|   |-- orchestrator.py       # Pipeline runner + Langfuse tracing
|   |-- state.py              # Shared agent state schema
|   |-- extraction_agent.py   # Claim parsing and entity extraction
|   |-- verification_agent.py # Cross-reference and credibility scoring
|   |-- risk_agent.py         # Risk assessment
|   |-- action_agent.py       # Response recommendations
|   |-- summary_agent.py      # Final report generation
|
|-- services/                 # Backend services
|   |-- db.py                 # SQLite database operations
|   |-- auth.py               # Login, logout, role management
|   |-- gemini.py             # Gemini LLM integration
|   |-- gnews.py              # GNews API live alerts
|   |-- ocr.py                # Tesseract OCR text extraction
|   |-- geo.py                # Geocoding (lat/lng lookup)
|   |-- langfuse_client.py    # Langfuse trace fetching
|   |-- config.py             # App configuration
|
|-- components/               # Streamlit UI components
|   |-- theme.py              # Global CSS theme
|   |-- layout.py             # Page wrapper
|   |-- cards.py              # Metric cards, verdict badges
|   |-- charts.py             # Plotly analytics charts
|   |-- map.py                # PyDeck crisis map
|   |-- alerts.py             # Live alert cards
|   |-- navbar.py             # Navigation bar
|
|-- pages/                    # Streamlit multi-page routing
    |-- user_login.py          # Citizen login
    |-- user_dashboard.py      # Citizen verification portal
    |-- authority_login.py     # Authority login
    |-- authority_dashboard.py # Authority command center
```

---

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO.git
cd YOUR-REPO
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and fill in your actual API keys:

```
GEMINI_API_KEY=your_key_here
GNEWS_API_KEY=your_key_here
LANGFUSE_PUBLIC_KEY=your_key_here
LANGFUSE_SECRET_KEY=your_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 5. Run the Application

```bash
streamlit run app.py
```

---

## Default Login Credentials

| Role | Username | Password |
|---|---|---|
| Citizen | user | user123 |
| Authority | admin | admin123 |

---

## Observability (Langfuse)

All 5 agents are automatically traced via native Langfuse callbacks during every pipeline execution. Traces appear as a structured waterfall in the Langfuse dashboard showing:

- Per-agent execution time
- Input/output at each node
- Final verdict, credibility, and risk scores
- Full trace ID linking

The Authority Dashboard includes a built-in AI Trace panel that surfaces the latest trace data directly in the UI.

---

## License

This project was built for educational and hackathon purposes.

# Aletheia — Crisis Information Verification & Intelligence System

Aletheia is a multi-agent AI system designed to help citizens and emergency authorities verify crisis-related claims, assess risk, detect repeated misinformation, and make faster, better-informed decisions during disasters.

The system takes a text claim or crisis-related screenshot, extracts the important details, cross-checks available evidence, separates physical disaster severity from misinformation risk, and presents the results through dedicated citizen and authority dashboards.

> **Built as a hackathon project with a focus on crisis intelligence, misinformation detection, explainable risk assessment, and emergency coordination.**

---

## What Aletheia Does

Aletheia is built around a simple problem:

**During a crisis, how do you determine what information can be trusted and what action should be taken?**

The system combines several specialized agents and supporting services to answer that question.

### Core capabilities

* **Multi-agent crisis analysis** using LangGraph
* **Crisis event and location extraction** from text and screenshots
* **Evidence-based verification** using news sources and corroboration
* **Cautious verification statuses** instead of treating every report as confirmed fact
* **Separate physical severity and misinformation risk scores**
* **Explainable risk calculations**
* **Duplicate claim detection** and viral misinformation cluster tracking
* **Citizen dashboard** for checking claims and screenshots
* **Authority dashboard** for triage, monitoring, and operational guidance
* **OCR support** using Tesseract with Gemini Vision fallback
* **Geospatial visualization** using PyDeck
* **Simulation/demo mode** with explicit `[SIMULATED]` labeling
* **Langfuse observability** for tracing and execution monitoring
* **Bcrypt password hashing** and removal of hardcoded API credentials

---

## How the System Works

Aletheia processes a crisis claim through a sequence of specialized components.

```text
User Claim / Screenshot
          |
          v
+-------------------------+
| Duplicate Claim Checker |
+-----------+-------------+
            |
            v
+---------------------------------------------+
|           LangGraph Agent Pipeline          |
|                                             |
|  +----------------+    +------------------+ |
|  | Extraction     | -> | Verification     | |
|  | Agent          |    | Agent            | |
|  +----------------+    +--------+---------+ |
|                                  |           |
|                                  v           |
|                       +------------------+   |
|                       | Risk Agent       |   |
|                       | Severity vs      |   |
|                       | Misinfo Risk     |   |
|                       +--------+---------+   |
|                                |             |
|                                v             |
|                       +------------------+   |
|                       | Action Agent     |   |
|                       | Citizen /        |   |
|                       | Authority        |   |
|                       +--------+---------+   |
|                                |             |
|                                v             |
|                       +------------------+   |
|                       | Summary Agent    |   |
|                       | Executive Brief  |   |
|                       +------------------+   |
+---------------------------------------------+
            |
            v
Citizen Dashboard + Authority Dashboard
            |
            v
      SQLite + PyDeck
```

---

## Agent Pipeline

| Agent                  | Responsibility                                                          | Main Output                                                                 |
| ---------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Extraction Agent**   | Identifies crisis type, location, date, and filters out non-crisis text | `event`, `location`, `date_context`, `is_crisis`                            |
| **Verification Agent** | Searches available evidence and evaluates corroboration                 | `verdict`, `credibility`, `evidence`, `trusted_sources`                     |
| **Risk Agent**         | Separates physical danger from misinformation harm                      | `physical_severity`, `misinformation_risk`, `composite_risk`, `explanation` |
| **Action Agent**       | Produces separate guidance for citizens and authorities                 | `citizen_action`, `authority_action`                                        |
| **Summary Agent**      | Produces an executive-level crisis briefing                             | `executive_summary`, `summary`                                              |

---

## Verification Statuses

Aletheia intentionally avoids treating a single news report as automatic proof.

Claims are categorized using four cautious statuses:

### `SUPPORTED`

The claim has corroborating evidence from multiple independent and credible sources.

### `CONTRADICTED`

Available evidence, such as official bulletins or reliable fact-checking sources, contradicts the claim.

### `UNVERIFIED`

There is not enough reliable evidence to confirm or reject the claim.

### `CONFLICTING`

Different sources provide contradictory information and further verification is required.

These statuses are designed to communicate uncertainty instead of presenting uncertain information as established fact.

---

## Explainable Risk Assessment

One of the main design decisions in Aletheia is to **separate physical disaster severity from misinformation risk**.

A serious earthquake and a false rumor about an earthquake are different problems and should not automatically receive the same risk interpretation.

Aletheia therefore calculates:

* **Physical Severity** — potential danger to people, infrastructure, and the surrounding area.
* **Misinformation Risk** — potential for a claim to cause panic, unnecessary evacuation, unsafe behavior, or other harmful reactions.
* **Operational Priority** — a combined triage signal used to help prioritize incidents.

The system also provides an explanation of the factors contributing to the calculated scores.

---

## Duplicate & Viral Claim Detection

Aletheia checks new claims against previously processed reports.

The duplicate detection system combines:

* TF-IDF cosine similarity
* Token Jaccard similarity
* Matching historical reports
* Cluster frequency

This helps identify when the same or highly similar rumor is being repeatedly submitted across different users or geographic areas.

---

## Citizen Portal

The Citizen Portal allows users to submit crisis information for verification.

Users can:

* Submit a text claim
* Upload a crisis-related screenshot
* View extracted event and location information
* See verification status
* Review evidence
* View credibility information
* See physical severity and misinformation risk separately
* Receive citizen safety guidance
* Get notified when a similar claim has already been investigated
* Check whether results contain simulated/demo data

### Demo Login

For trying the application locally, the demo Citizen Portal credentials are:

```text
Username: user
Password: user123
```

> **Demo credentials only:** These credentials are intended for the included demo environment and must be changed or replaced before deploying the application in a real production environment.

---

## Authority Command Center

The Authority Command Center provides a broader view of incoming crisis reports.

It includes:

* Crisis triage
* Risk metrics
* Verification status breakdowns
* Geospatial visualization
* Priority categorization
* Evidence and source information
* Simulation/demo indicators
* Operational recommendations
* Langfuse execution and trace information

### Demo Login

For trying the application locally:

```text
Username: admin
Password: admin123
```

> **Demo credentials only:** These credentials are included for local demonstration purposes and are not suitable for a production deployment.

---

## OCR & Screenshot Verification

Aletheia can extract text from crisis screenshots.

The OCR pipeline supports:

1. OpenCV image preprocessing
2. Local Tesseract OCR
3. Automatic Gemini Vision fallback when Tesseract is unavailable

This makes screenshot-based verification usable even when a local Tesseract installation is not available, provided a Gemini API key is configured.

For offline/local OCR, Tesseract can be installed separately.

---

## Simulation & Demo Mode

External APIs may not always be available during development or demonstrations.

Aletheia therefore includes a fallback system for demo scenarios.

Synthetic results are explicitly marked with:

```text
[SIMULATED]
```

and include simulation metadata so that demo information is not silently presented as live evidence.

This is particularly useful when the GNews API quota is unavailable or when the project is being demonstrated without external API credentials.

---

## Observability

Aletheia integrates Langfuse for agent observability.

The system can track:

* Agent execution
* Node status
* Execution latency
* Trace IDs
* Pipeline behavior

This makes it easier to understand how a crisis claim moved through the multi-agent pipeline.

---

## Tech Stack

### Frontend

* Streamlit
* Custom CSS
* Plotly
* PyDeck

### AI & Agent Orchestration

* LangGraph
* LangChain
* Google Gemini API

### News Intelligence

* GNews API v4
* Simulated benchmark fallback

### OCR & Computer Vision

* OpenCV
* Pillow
* PyTesseract
* Gemini Multimodal Vision

### Data & Similarity

* SQLite
* sqlite-utils
* scikit-learn
* NumPy
* Pandas

### Geospatial

* PyDeck
* GeoPy
* Nominatim

### Security

* bcrypt
* Environment-based secrets

### Observability

* Langfuse



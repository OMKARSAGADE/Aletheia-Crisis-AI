"""GNews API Service for Crisis Monitoring.
Fetches real-time news articles or returns explicitly labeled simulated data
when API keys are unconfigured, rate-limited, or in DEMO mode.
"""
import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

def get_gnews_api_key() -> str:
    key = os.getenv("GNEWS_API_KEY", "").strip()
    if key in ["your_gnews_api_key_here", "disabled", "none", ""]:
        return ""
    return key

def is_demo_mode() -> bool:
    return os.getenv("DEMO_MODE", "false").lower() in ["true", "1", "yes"]

def fetch_live_alerts(limit: int = 10) -> List[Dict[str, Any]]:
    """Fetch live alerts from GNews or return labeled simulated alerts."""
    api_key = get_gnews_api_key()
    
    if not api_key or is_demo_mode():
        return get_fallback_alerts(limit)
        
    url = "https://gnews.io/api/v4/search"
    query = "(flood OR fire OR earthquake OR accident OR collapse OR emergency OR cyclone)"
    params = {
        "q": query,
        "lang": "en",
        "country": "in",
        "max": limit,
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=8)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            results = []
            for article in articles:
                results.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", "News Outlet"),
                    "publishedAt": article.get("publishedAt", datetime.now().isoformat()),
                    "url": article.get("url", "#"),
                    "location": "India",
                    "is_simulated": False
                })
            if results:
                try:
                    from services.db import save_alerts
                    save_alerts(results)
                except Exception:
                    pass
                return results
    except Exception as e:
        print(f"GNews API Live Fetch Warning: {e}")
        
    return get_fallback_alerts(limit)

def get_fallback_alerts(limit: int = 5) -> List[Dict[str, Any]]:
    """Return synthetic alerts explicitly marked as [SIMULATED]."""
    now_iso = datetime.now().isoformat()
    return [
        {
            "title": "[SIMULATED] Heavy monsoon rainfall prompts alert in coastal river basins",
            "description": "State disaster management authority monitors water discharge levels.",
            "source": "Simulated Wire (Demo)",
            "publishedAt": now_iso,
            "url": "#",
            "location": "Coastal Region",
            "is_simulated": True
        },
        {
            "title": "[SIMULATED] Fire department brings commercial warehouse blaze under control",
            "description": "Six fire tenders dispatched to site; no civilian casualties reported.",
            "source": "Simulated Wire (Demo)",
            "publishedAt": now_iso,
            "url": "#",
            "location": "Pune",
            "is_simulated": True
        },
        {
            "title": "[SIMULATED] Precautionary structural safety review for older flyovers",
            "description": "Municipal engineering wing conducts load-bearing assessment.",
            "source": "Simulated Wire (Demo)",
            "publishedAt": now_iso,
            "url": "#",
            "location": "Mumbai",
            "is_simulated": True
        }
    ][:limit]

def search_specific_incident(event: Optional[str], location: Optional[str], date_context: str = "Recent") -> List[Dict[str, Any]]:
    """Search for news articles matching an extracted crisis incident and location."""
    if not event and not location:
        return []

    api_key = get_gnews_api_key()
    if not api_key or is_demo_mode():
        return simulate_gnews_results(event, location)
        
    url = "https://gnews.io/api/v4/search"
    query_parts = []
    if event:
        query_parts.append(event)
    if location and location.lower() != "unknown":
        query_parts.append(location)
    if date_context and date_context.lower() not in ["recent", "none", ""]:
        query_parts.append(date_context)
        
    query = " ".join(query_parts)
    params = {
        "q": query,
        "lang": "en",
        "country": "in",
        "max": 10,
        "sortby": "publishedAt",
        "apikey": api_key
    }
    
    try:
        response = requests.get(url, params=params, timeout=8)
        if response.status_code in [403, 429]:
            print("GNews API quota reached or key invalid. Falling back to clearly labeled simulation.")
            return simulate_gnews_results(event, location)
            
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            results = []
            for article in articles:
                results.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", {}).get("name", "News Outlet"),
                    "url": article.get("url", "#"),
                    "publishedAt": article.get("publishedAt", ""),
                    "is_simulated": False
                })
            return results
    except Exception as e:
        print(f"GNews API Search Error: {e}")
        
    return simulate_gnews_results(event, location)

def simulate_gnews_results(event: Optional[str], location: Optional[str]) -> List[Dict[str, Any]]:
    """Generate clearly marked simulated news findings for demo scenarios."""
    if not event or not location or location.lower() in ["unknown", "none", ""]:
        return []
        
    evt_title = event.title()
    loc_title = location.title()
    now_iso = datetime.now().isoformat()
    
    # Common test benchmark events (e.g. Hingoli earthquake, Pune fire)
    if evt_title.lower() in ["earthquake", "fire", "flood", "cyclone", "collapse"]:
        return [
            {
                "title": f"[SIMULATED EVIDENCE] Regional agencies respond to {evt_title} reports in {loc_title}",
                "source": "Simulated Press Wire (Demo)",
                "url": "#",
                "publishedAt": now_iso,
                "is_simulated": True
            },
            {
                "title": f"[SIMULATED EVIDENCE] Disaster control room issues preliminary bulletin for {loc_title} {evt_title.lower()}",
                "source": "Municipal Bulletin (Demo)",
                "url": "#",
                "publishedAt": now_iso,
                "is_simulated": True
            }
        ]
    return []

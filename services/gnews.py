import os
import requests
from datetime import datetime
from services.db import save_alerts

GNEWS_API_KEY = os.getenv("GNEWS_API_KEY")

def fetch_live_alerts(limit=10):
    if not GNEWS_API_KEY or GNEWS_API_KEY == "your_gnews_api_key_here":
        return get_fallback_alerts(limit)
        
    url = "https://gnews.io/api/v4/search"
    query = "(flood OR fire OR earthquake OR accident OR collapse OR emergency OR cyclone)"
    params = {
        "q": query,
        "lang": "en",
        "country": "in", # Focusing on India for this demo
        "max": limit,
        "apikey": GNEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        articles = data.get("articles", [])
        results = []
        for article in articles:
            results.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "source": article.get("source", {}).get("name", "Unknown Source"),
                "publishedAt": article.get("publishedAt", datetime.now().isoformat()),
                "url": article.get("url", ""),
                "location": "Unknown" # GNews doesn't typically provide exact geo-coords
            })
            
        if results:
            # Save to DB dynamically
            save_alerts(results)
            
        return results if results else get_fallback_alerts(limit)
        
    except Exception as e:
        print(f"GNews API Error: {e}")
        return get_fallback_alerts(limit)

def get_fallback_alerts(limit):
    # Mock data fallback
    return [
        {
            "title": "[MOCK] Heavy rains trigger flood warnings in coastal districts",
            "description": "Authorities advise caution as water levels rise rapidly.",
            "source": "Local News Mock",
            "publishedAt": datetime.now().isoformat(),
            "url": "#",
            "location": "Unknown"
        },
        {
            "title": "[MOCK] Industrial fire controlled after 4 hours",
            "description": "No casualties reported in the warehouse blaze.",
            "source": "City Reports",
            "publishedAt": datetime.now().isoformat(),
            "url": "#",
            "location": "Unknown"
        }
    ][:limit]

def search_specific_incident(event, location, date_context="Recent"):
    if not GNEWS_API_KEY or GNEWS_API_KEY == "your_gnews_api_key_here":
        # Simulate API payload for demo if key missing
        return simulate_gnews_results(event, location)
        
    url = "https://gnews.io/api/v4/search"
    
    # Unshackled query: Let the search engine find relevance naturally without strict quotes
    query = f"{event} {location}"
    if date_context.lower() != "recent":
        query += f" {date_context}"
        
    params = {
        "q": query,
        "lang": "en",
        "country": "in",
        "max": 10,
        "sortby": "publishedAt",
        "apikey": GNEWS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        
        # If rate limited (429) or forbidden (403), gracefully simulate so demo doesn't crash
        if response.status_code in [403, 429]:
            return simulate_gnews_results(event, location)
            
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", [])
            results = []
            for article in articles:
                results.append({
                    "title": article.get("title", ""),
                    "source": article.get("source", {}).get("name", "Unknown Source"),
                    "url": article.get("url", ""),
                    "publishedAt": article.get("publishedAt", "")
                })
            return results
    except Exception as e:
        print(f"GNews API Search Error: {e}")
    return []

def simulate_gnews_results(event, location):
    # If the user asks about a common demo scenario, simulate a hit
    if event.lower() in ["fire", "earthquake", "flood", "collapse"] and location.lower() not in ["unknown", ""]:
        return [
            {
                "title": f"Breaking: {event.title()} reported in {location.title()}",
                "source": "Simulated News Network",
                "url": "#",
                "publishedAt": datetime.now().isoformat()
            },
            {
                "title": f"Emergency services respond to {location.title()} {event.lower()}",
                "source": "Local Updates",
                "url": "#",
                "publishedAt": datetime.now().isoformat()
            }
        ]
    return []

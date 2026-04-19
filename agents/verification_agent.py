import random
from services.gnews import search_specific_incident
from services.gemini import model

def run_verification(state):
    extracted = state.get("extracted_data", {})
    event = extracted.get("event", "incident")
    location = extracted.get("location", "Unknown")
    date_context = extracted.get("date_context", "Recent")
    
   
    if location == "Unknown":
        state["verification_result"] = {
            "verdict": "UNVERIFIED",
            "credibility": random.randint(10, 30),
            "trusted_sources": [],
            "evidence": "No specific location provided in the claim."
        }
        return state
        
  
    raw_articles = search_specific_incident(event, location, date_context)
    
   
    articles = _filter_relevant_articles(raw_articles, event, location)
    
   
    if not articles:
        from services.db import get_recent_alerts
        recent_alerts = get_recent_alerts(50)
        for alert in recent_alerts:
            alert_title = alert.get("title", "").lower()
            event_synonyms = _get_event_synonyms(event.lower())
            if any(syn in alert_title for syn in event_synonyms) and location.lower() in alert_title:
                articles.append({
                    "name": alert.get("source", "Historical Alert"),
                    "title": alert.get("title", ""),
                    "url": alert.get("url", "#")
                })
                if len(articles) >= 2: break
                
    article_count = len(articles)
    
    trusted_sources = []
    for art in articles:
        trusted_sources.append({
            "name": art.get("source", art.get("name", "News Article")),
            "desc": art.get("title", ""),
            "url": art.get("url", "#")
        })
        
    if article_count >= 3:
        credibility = random.randint(85, 95)
        verdict = "Likely Real"
        evidence = f"Found 3 matching GNews articles confirming {event} in {location} ({date_context})."
    elif article_count == 2:
        credibility = random.randint(65, 80)
        verdict = "Likely Real"
        evidence = f"Found 2 matching GNews articles confirming {event} in {location} ({date_context})."
    elif article_count == 1:
        credibility = random.randint(40, 60)
        verdict = "Needs Verification"
        evidence = f"Found only 1 article related to {event} in {location} ({date_context}). Proceed with caution."
    else:
        credibility = random.randint(10, 30)
        verdict = "Unverified"
        evidence = f"Found 0 relevant news articles confirming {event} in {location} ({date_context})."
        
    state["verification_result"] = {
        "verdict": verdict,
        "credibility": credibility,
        "trusted_sources": trusted_sources,
        "evidence": evidence
    }
    
    return state

def _filter_relevant_articles(raw_articles, event, location):
    """Filter articles to only keep those genuinely about the crisis event, not metaphorical usage."""
    if not raw_articles:
        return []
    
    
    if model:
        try:
            titles = "\n".join([f"- {a.get('title', '')}" for a in raw_articles[:10]])
            prompt = f"""I am searching for news about an actual '{event}' disaster/crisis in '{location}'.
Below are article titles returned by a news search. Some may use the word '{event}' metaphorically (e.g., 'flood of voters') rather than referring to an actual disaster.

Articles:
{titles}

Reply with ONLY the line numbers (1-indexed, comma-separated) of articles that are genuinely about an actual {event} disaster/emergency in {location}. If none are relevant, reply 'NONE'."""
            response = model.generate_content(prompt)
            answer = response.text.strip()
            
            if answer.upper() == "NONE":
                return []
            
           
            relevant = []
            for num_str in answer.replace(" ", "").split(","):
                try:
                    idx = int(num_str) - 1
                    if 0 <= idx < len(raw_articles):
                        relevant.append(raw_articles[idx])
                except ValueError:
                    continue
            return relevant[:3]  
        except Exception as e:
            print(f"Gemini relevance filter error: {e}")
    
    
    articles = []
    event_synonyms = _get_event_synonyms(event.lower())
    disaster_indicators = ["disaster", "emergency", "casualties", "rescue", "evacuated", 
                          "dead", "injured", "relief", "damage", "warning", "alert",
                          "struck", "hit", "affected", "ravaged", "devastated",
                          "magnitude", "tremor", "blaze", "inferno", "submerged",
                          "waterlogging", "landfall", "crisis", "toll"]
    
    
    metaphor_patterns = ["flood of ", "flood in votes", "flooded with", "fire in the belly",
                        "under fire for", "fire sale", "earthquake in politics",
                        "political earthquake", "collapse of ", "collapse in polls"]
    
    for art in raw_articles:
        title = art.get("title", "").lower()
        
    
        if any(mp in title for mp in metaphor_patterns):
            continue
            
        location_match = location.lower() in title
        event_match = any(syn in title for syn in event_synonyms)
        disaster_context = any(ind in title for ind in disaster_indicators)
        
        if location_match and event_match and disaster_context:
            articles.append(art)
    
    return articles[:3]

def _get_event_synonyms(event):
    """Return a list of keywords that indicate an article is truly about this crisis type."""
    synonyms = {
        "flood": ["flood", "flooding", "submerged", "waterlogging", "deluge", "inundation"],
        "earthquake": ["earthquake", "quake", "seismic", "tremor", "magnitude", "jolted"],
        "fire": ["fire", "blaze", "inferno", "arson", "engulfed", "gutted"],
        "cyclone": ["cyclone", "hurricane", "typhoon", "storm", "landfall"],
        "collapse": ["collapse", "collapsed", "cave-in", "crumbled", "structural failure"],
        "accident": ["accident", "crash", "collision", "derailment", "pile-up"],
        "riot": ["riot", "violence", "clashes", "unrest", "protest"],
        "blast": ["blast", "explosion", "detonation", "bomb"],
        "leak": ["leak", "gas leak", "chemical", "spill", "toxic"],
    }
    return synonyms.get(event, [event])

"""Verification Agent: Cross-references claims against news intelligence feeds
and historical alerts, assigning deterministic credibility scores and cautious statuses.
"""
from typing import Dict, Any, List, Optional
from services.gnews import search_specific_incident
from services.gemini import get_model

def run_verification(state: Dict[str, Any]) -> Dict[str, Any]:
    extracted = state.get("extracted_data", {})
    is_crisis = extracted.get("is_crisis", True)
    event = extracted.get("event")
    location = extracted.get("location")
    date_context = extracted.get("date_context", "Recent")
    raw_text = state.get("input_text", "")
    
    # Non-crisis text
    if not is_crisis or not event:
        state["verification_result"] = {
            "status": "completed",
            "verdict": "UNVERIFIED",
            "credibility": 15,
            "trusted_sources": [],
            "evidence": "No clear crisis or emergency event detected in the provided text.",
            "has_simulated_sources": False
        }
        return state

    # Missing location
    if not location or location.lower() in ["unknown", "none", ""]:
        state["verification_result"] = {
            "status": "completed",
            "verdict": "UNVERIFIED",
            "credibility": 25,
            "trusted_sources": [],
            "evidence": f"Claim references a {event} but provides no specific verifiable location.",
            "has_simulated_sources": False
        }
        return state

    # Search news intelligence
    raw_articles = search_specific_incident(event, location, date_context)
    articles = _filter_relevant_articles(raw_articles, event, location)

    # Check local database alerts if live news had no hits
    if not articles:
        try:
            from services.db import get_recent_alerts
            recent_alerts = get_recent_alerts(50)
            for alert in recent_alerts:
                alert_title = alert.get("title", "").lower()
                event_synonyms = _get_event_synonyms(event.lower())
                if any(syn in alert_title for syn in event_synonyms) and location.lower() in alert_title:
                    articles.append({
                        "name": alert.get("source", "Historical Alert"),
                        "title": alert.get("title", ""),
                        "url": alert.get("url", "#"),
                        "is_simulated": alert.get("is_simulated", False)
                    })
                    if len(articles) >= 2:
                        break
        except Exception:
            pass

    article_count = len(articles)
    trusted_sources = []
    has_simulated = False
    for art in articles:
        is_sim = art.get("is_simulated", False)
        if is_sim:
            has_simulated = True
        trusted_sources.append({
            "name": art.get("source", art.get("name", "News Outlet")),
            "desc": art.get("title", ""),
            "url": art.get("url", "#"),
            "is_simulated": is_sim
        })

    # Cautious status evaluation (Supported, Contradicted, Unverified, Conflicting)
    text_lower = raw_text.lower()
    is_explicit_rumor_or_fake = any(w in text_lower for w in ["rumor", "fake alert", "hoax", "false alarm"])
    
    if is_explicit_rumor_or_fake and article_count == 0:
        verdict = "CONTRADICTED"
        credibility = 10
        evidence = f"Claim identified as potential rumor with 0 corroborating news reports for {event} in {location}."
    elif article_count >= 3:
        verdict = "SUPPORTED"
        credibility = 88
        evidence = f"Corroborated by 3 independent news reports referencing {event} in {location} ({date_context})."
    elif article_count == 2:
        verdict = "SUPPORTED"
        credibility = 72
        evidence = f"Corroborated by 2 news reports referencing {event} in {location} ({date_context})."
    elif article_count == 1:
        verdict = "UNVERIFIED"
        credibility = 48
        evidence = f"Found only 1 preliminary news reference for {event} in {location}. Secondary confirmation needed."
    else:
        verdict = "UNVERIFIED"
        credibility = 20
        evidence = f"Found 0 corroborating news reports for {event} in {location} ({date_context})."

    if has_simulated:
        evidence += " [Evidence gathered from simulated demo feeds]"

    state["verification_result"] = {
        "status": "completed",
        "verdict": verdict,
        "credibility": credibility,
        "trusted_sources": trusted_sources,
        "evidence": evidence,
        "article_count": article_count,
        "has_simulated_sources": has_simulated
    }
    return state

def _filter_relevant_articles(raw_articles: List[Dict[str, Any]], event: str, location: str) -> List[Dict[str, Any]]:
    """Filter articles to only keep those genuinely about the disaster, eliminating metaphorical usages."""
    if not raw_articles:
        return []
        
    model = get_model()
    if model:
        try:
            titles = "\n".join([f"- {a.get('title', '')}" for a in raw_articles[:10]])
            prompt = (
                f"I am verifying claims about an actual '{event}' emergency in '{location}'.\n"
                f"Below are article headlines:\n{titles}\n\n"
                f"Reply ONLY with the 1-indexed line numbers (comma-separated) of headlines that genuinely report "
                f"on this actual disaster/incident. If none are relevant, reply 'NONE'."
            )
            response = model.generate_content(prompt)
            answer = response.text.strip()
            
            if answer.upper() != "NONE":
                relevant = []
                for num_str in answer.replace(" ", "").split(","):
                    try:
                        idx = int(num_str) - 1
                        if 0 <= idx < len(raw_articles):
                            relevant.append(raw_articles[idx])
                    except ValueError:
                        continue
                if relevant:
                    return relevant[:3]
        except Exception as e:
            print(f"LLM relevance filter warning: {e}")

    # Fallback heuristic filter
    articles = []
    event_synonyms = _get_event_synonyms(event.lower())
    disaster_indicators = [
        "disaster", "emergency", "casualties", "rescue", "evacuated",
        "dead", "injured", "relief", "damage", "warning", "alert",
        "struck", "hit", "affected", "ravaged", "devastated",
        "magnitude", "tremor", "blaze", "inferno", "submerged",
        "waterlogging", "landfall", "crisis", "toll", "incident", "hospital"
    ]
    metaphor_patterns = [
        "flood of ", "flood in votes", "flooded with", "fire in the belly",
        "under fire for", "fire sale", "political earthquake", "collapse in polls"
    ]

    for art in raw_articles:
        title = art.get("title", "").lower()
        if any(mp in title for mp in metaphor_patterns):
            continue
            
        location_match = location.lower() in title or "india" in title or art.get("is_simulated", False)
        event_match = any(syn in title for syn in event_synonyms)
        disaster_context = any(ind in title for ind in disaster_indicators) or art.get("is_simulated", False)
        
        if event_match and (location_match or disaster_context):
            articles.append(art)

    return articles[:3]

def _get_event_synonyms(event: str) -> List[str]:
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
        "landslide": ["landslide", "mudslide", "rockfall"]
    }
    return synonyms.get(event, [event])

"""Extraction Agent: Extracts crisis event type, geographic location,
and temporal context from user-submitted text or OCR output.
"""
import re
from typing import Optional, Dict, Any
from services.gemini import get_model

# Comprehensive crisis dictionary mapping synonyms to canonical crisis types
CRISIS_KEYWORDS = {
    "Earthquake": ["earthquake", "quake", "seismic", "tremor", "aftershock"],
    "Flood": ["flood", "flooding", "waterlogging", "submerged", "deluge", "inundation"],
    "Fire": ["fire", "blaze", "inferno", "arson", "engulfed", "gutted"],
    "Cyclone": ["cyclone", "hurricane", "typhoon", "storm", "landfall", "tornado"],
    "Collapse": ["collapse", "collapsed", "bridge collapse", "building collapse", "cave-in", "crumbled"],
    "Accident": ["accident", "collision", "derailment", "train crash", "plane crash", "pile-up"],
    "Blast": ["blast", "explosion", "bomb", "detonation", "ied"],
    "Leak": ["gas leak", "chemical leak", "toxic spill", "radiation leak", "pipeline leak"],
    "Riot": ["riot", "communal violence", "clashes", "civil unrest", "mob violence"],
    "Landslide": ["landslide", "mudslide", "rockfall"],
    "Tsunami": ["tsunami", "tidal wave"]
}

# Common known geographic entities (priority recognition for India and major global hubs)
KNOWN_LOCATIONS = [
    "Pimpri Chinchwad", "Pimpri", "Chinchwad", "Pune", "Mumbai", "Delhi", "New Delhi",
    "Chennai", "Kolkata", "Bengaluru", "Bangalore", "Hyderabad", "Ahmedabad", "Nagpur",
    "Hingoli", "Nashik", "Thane", "Assam", "Guwahati", "Kerala", "Uttarakhand",
    "Himachal", "Gujarat", "Odisha", "Bhubaneswar", "Jaipur", "Lucknow", "Patna",
    "Bhopal", "Chandigarh", "Srinagar", "Kashmir", "Manipur", "Goa"
]

MONTHS = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
    "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec"
]

def run_extraction(state: Dict[str, Any]) -> Dict[str, Any]:
    raw_text = state.get("input_text", "")
    text_lower = raw_text.lower()
    
    found_event: Optional[str] = None
    found_location: Optional[str] = None
    found_date: str = "Recent"
    is_crisis: bool = False
    
    # 1. Attempt structured LLM extraction if Gemini model is available
    model = get_model()
    if model:
        try:
            prompt = (
                f"Analyze this text to determine if it describes a crisis, disaster, emergency, or accident claim.\n"
                f"If it does NOT describe any crisis/emergency/incident, respond strictly with 'NO_CRISIS|None|None'.\n"
                f"If it DOES describe a crisis, extract: Event Type (e.g. Earthquake, Flood, Fire, Collapse) | "
                f"Location (City, District, or State) | Date Context (e.g. 'April 2026', 'Today', or 'Recent').\n"
                f"Reply STRICTLY in the format 'Event|Location|Date' without any extra words.\n"
                f"Text: '{raw_text}'"
            )
            response = model.generate_content(prompt)
            reply = response.text.strip().replace("`", "")
            
            if "NO_CRISIS" in reply.upper():
                found_event = None
                found_location = None
                is_crisis = False
            else:
                parts = [p.strip() for p in reply.split('|')]
                if len(parts) >= 2:
                    evt = parts[0].title() if parts[0] and parts[0].lower() not in ["none", "unknown", ""] else None
                    loc = parts[1].title() if parts[1] and parts[1].lower() not in ["none", "unknown", ""] else None
                    dt = parts[2] if len(parts) >= 3 and parts[2] and parts[2].lower() not in ["none", ""] else "Recent"
                    
                    if evt and evt.lower() not in ["none", "no crisis", "non-crisis"]:
                        found_event = evt
                        found_location = loc
                        found_date = dt
                        is_crisis = True
        except Exception as e:
            # Fall back to rule-based parser on any LLM failure or timeout
            pass

    # 2. Rule-based extraction (used as fallback or primary when LLM is unavailable)
    if found_event is None and not is_crisis:
        # Check crisis keywords
        for canonical_event, synonyms in CRISIS_KEYWORDS.items():
            for syn in synonyms:
                pattern = r'\b' + re.escape(syn) + r'\b'
                if re.search(pattern, text_lower):
                    found_event = canonical_event
                    is_crisis = True
                    break
            if is_crisis:
                break
                
        # If no crisis detected at all, do NOT fabricate location or event
        if not is_crisis:
            state["extracted_data"] = {
                "status": "completed",
                "is_crisis": False,
                "event": None,
                "location": None,
                "date_context": "Recent"
            }
            return state

    # Extract location if event was detected
    if is_crisis and not found_location:
        # Check known location list (multi-word first)
        sorted_locations = sorted(KNOWN_LOCATIONS, key=len, reverse=True)
        for loc in sorted_locations:
            pattern = r'\b' + re.escape(loc.lower()) + r'\b'
            if re.search(pattern, text_lower):
                found_location = loc
                break

    # If still not found, check prepositional patterns: "in <City>", "at <City>", "near <City>"
    if is_crisis and not found_location:
        prep_match = re.search(r'\b(?:in|at|near|around)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)', raw_text)
        if prep_match:
            candidate = prep_match.group(1).strip()
            # Ignore false positives like "in April" or "in Hospital"
            if candidate.lower() not in MONTHS and candidate.lower() not in ["the", "a", "an", "today", "yesterday", "recent"]:
                found_location = candidate.title()

    # Extract date context if still "Recent"
    if found_date == "Recent":
        # Check for month + year: e.g. "April 2026", "Oct 2025"
        date_match = re.search(r'\b(' + '|'.join(MONTHS) + r')\s+(\d{4})\b', text_lower)
        if date_match:
            found_date = f"{date_match.group(1).title()} {date_match.group(2)}"
        else:
            # Check standalone 4-digit year
            year_match = re.search(r'\b(202[0-9])\b', text_lower)
            if year_match:
                found_date = year_match.group(1)

    state["extracted_data"] = {
        "status": "completed",
        "is_crisis": is_crisis,
        "event": found_event,
        "location": found_location,
        "date_context": found_date
    }
    return state

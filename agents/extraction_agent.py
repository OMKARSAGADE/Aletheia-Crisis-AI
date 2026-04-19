import re
from services.gemini import model

def run_extraction(state):
    text_lower = state.get("input_text", "").lower()
    
    found_event = "incident"
    found_location = "Unknown"
    found_date = "Recent"
    
  
    if model:
        try:
            prompt = f"Extract the primary crisis event type, the location city/state, and the date/time context from this text. If no specific date is mentioned, reply 'Recent'. Reply STRICTLY in this format 'Event|Location|Date'. Text: '{text_lower}'"
            response = model.generate_content(prompt)
            parts = response.text.strip().split('|')
            if len(parts) >= 3:
                found_event = parts[0].strip().title()
                found_location = parts[1].strip().title()
                found_date = parts[2].strip()
            elif len(parts) == 2:
                found_event = parts[0].strip().title()
                found_location = parts[1].strip().title()
        except Exception as e:
            print(f"Extraction Agent Gemini Error: {e}")
            
   
    if found_event == "incident" and found_location == "Unknown":
        events = ["earthquake", "flood", "fire", "accident", "collapse", "cyclone", "riot", "blast", "leak"]
        for e in events:
            if e in text_lower:
                found_event = e.title()
                break
                
      
        
        skip_words = set(events + ["the", "a", "an", "in", "at", "on", "of", "to", "is",
                                   "urgent", "breaking", "demo", "scenario", "near",
                                   "reported", "happening", "now", "evacuate", "help",
                                   "please", "alert", "warning"])
        words = state.get("input_text", "").split()
        for w in words:
            clean_w = re.sub(r'[^a-zA-Z]', '', w)
            if len(clean_w) > 1 and clean_w.lower() not in skip_words:
                found_location = clean_w.title()
                break

    state["extracted_data"] = {
        "status": "completed", 
        "event": found_event,
        "location": found_location,
        "date_context": found_date
    }
    return state

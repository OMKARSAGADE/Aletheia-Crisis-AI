import sqlite_utils
from datetime import datetime
from .config import DB_PATH

def get_connection():
    return sqlite_utils.Database(DB_PATH)

def init_db():
    db = get_connection()
    # Create users table
    if "users" not in db.table_names():
        db["users"].create({
            "username": str,
            "password": str,
            "role": str
        }, pk="username")
    
    # Safely migrate reports table to include location
    if "reports" not in db.table_names():
        db["reports"].create({
            "id": int,
            "input_text": str,
            "verdict": str,
            "credibility_score": int,
            "risk_score": int,
            "location": str,
            "timestamp": str,
            "source_type": str
        }, pk="id")
    else:
        if "location" not in db["reports"].columns_dict:
            db["reports"].add_column("location", str)
        
    # Create logs table
    if "logs" not in db.table_names():
        db["logs"].create({
            "id": int,
            "event": str,
            "timestamp": str
        }, pk="id")
        
    # Create alerts table for GNews API
    if "alerts" not in db.table_names():
        db["alerts"].create({
            "id": int,
            "title": str,
            "description": str,
            "source": str,
            "publishedAt": str,
            "url": str,
            "location": str,
            "fetched_at": str
        }, pk="id")
        
    seed_users()
    seed_demo_reports()

def seed_users():
    db = get_connection()
    users = db["users"]
    
    if users.count == 0:
        users.insert_all([
            {"username": "user", "password": "user123", "role": "user"},
            {"username": "admin", "password": "admin123", "role": "authority"}
        ], ignore=True)

def seed_demo_reports():
    db = get_connection()
    reports = db["reports"]
    
    # Only seed if empty to provide initial map data
    if reports.count == 0:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reports.insert_all([
            {
                "input_text": "Flood rumor in Pimpri Chinchwad, evacuate now!",
                "verdict": "FAKE",
                "credibility_score": 15,
                "risk_score": 90,
                "location": "Pimpri Chinchwad",
                "timestamp": timestamp,
                "source_type": "text"
            },
            {
                "input_text": "Massive fire reported near Pune station.",
                "verdict": "REAL",
                "credibility_score": 95,
                "risk_score": 85,
                "location": "Pune",
                "timestamp": timestamp,
                "source_type": "image"
            },
            {
                "input_text": "Road collapse warning issued in Mumbai by traffic police.",
                "verdict": "UNVERIFIED",
                "credibility_score": 55,
                "risk_score": 60,
                "location": "Mumbai",
                "timestamp": timestamp,
                "source_type": "text"
            }
        ])

def force_seed_demo_reports():
    db = get_connection()
    reports = db["reports"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reports.insert_all([
        {
            "input_text": "[DEMO] Urgent flood evacuation triggered in Pimpri Chinchwad!",
            "verdict": "FAKE",
            "credibility_score": 10,
            "risk_score": 95,
            "location": "Pimpri Chinchwad",
            "timestamp": timestamp,
            "source_type": "text"
        },
        {
            "input_text": "[DEMO] Massive industrial fire reported near Pune station.",
            "verdict": "REAL",
            "credibility_score": 98,
            "risk_score": 85,
            "location": "Pune",
            "timestamp": timestamp,
            "source_type": "image"
        },
        {
            "input_text": "[DEMO] Traffic police warn of bridge collapse in Mumbai.",
            "verdict": "UNVERIFIED",
            "credibility_score": 50,
            "risk_score": 65,
            "location": "Mumbai",
            "timestamp": timestamp,
            "source_type": "text"
        }
    ])

def save_report(input_text, verdict, credibility_score, risk_score, source_type="text", location="Unknown"):
    db = get_connection()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["reports"].insert({
        "input_text": input_text,
        "verdict": verdict,
        "credibility_score": credibility_score,
        "risk_score": risk_score,
        "location": location,
        "timestamp": timestamp,
        "source_type": source_type
    })

def get_recent_reports(limit=5):
    db = get_connection()
    return list(db.query(f"SELECT * FROM reports ORDER BY id DESC LIMIT {limit}"))

def get_kpi_metrics():
    db = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    total_today = list(db.query(f"SELECT COUNT(*) as count FROM reports WHERE timestamp LIKE '{today}%'"))[0]['count']
    high_risk = list(db.query("SELECT COUNT(*) as count FROM reports WHERE risk_score > 70"))[0]['count']
    fake_claims = list(db.query("SELECT COUNT(*) as count FROM reports WHERE LOWER(verdict) = 'fake'"))[0]['count']
    hotspots = list(db.query("SELECT COUNT(DISTINCT location) as count FROM reports WHERE location IS NOT NULL AND location != 'Unknown'"))[0]['count']
    
    return total_today, high_risk, fake_claims, hotspots

def get_live_feed(limit=10):
    db = get_connection()
    return list(db.query(f"SELECT * FROM reports ORDER BY id DESC LIMIT {limit}"))

def get_priority_incidents(limit=10):
    db = get_connection()
    return list(db.query(f"SELECT * FROM reports ORDER BY risk_score DESC, timestamp DESC LIMIT {limit}"))

def get_unverified_queue():
    db = get_connection()
    # Fetch reports needing manual review: unverified OR low confidence
    return list(db.query("SELECT * FROM reports WHERE LOWER(verdict) = 'unverified' OR credibility_score < 40 ORDER BY id DESC"))

def inject_scenario(scenario_type):
    db = get_connection()
    reports = db["reports"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if scenario_type == "Flood Rumor":
        reports.insert({
            "input_text": "[SCENARIO] Urgent flood evacuation triggered in Pimpri Chinchwad!",
            "verdict": "FAKE",
            "credibility_score": 10,
            "risk_score": 95,
            "location": "Pimpri Chinchwad",
            "timestamp": timestamp,
            "source_type": "text"
        })
    elif scenario_type == "Fire Incident":
        reports.insert({
            "input_text": "[SCENARIO] Massive industrial fire reported near Pune station.",
            "verdict": "REAL",
            "credibility_score": 98,
            "risk_score": 85,
            "location": "Pune",
            "timestamp": timestamp,
            "source_type": "image"
        })
    elif scenario_type == "Collapse Warning":
        reports.insert({
            "input_text": "[SCENARIO] Traffic police warn of bridge collapse in Mumbai.",
            "verdict": "UNVERIFIED",
            "credibility_score": 50,
            "risk_score": 65,
            "location": "Mumbai",
            "timestamp": timestamp,
            "source_type": "text"
        })

def get_all_reports():
    db = get_connection()
    return list(db.query("SELECT * FROM reports"))

def save_alerts(alerts_list):
    if not alerts_list:
        return
    db = get_connection()
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for alert in alerts_list:
        alert['fetched_at'] = fetched_at
        
    # Using insert_all with ignore=True in case of duplicates (if we use URL as ID later, currently auto-increment)
    db["alerts"].insert_all(alerts_list, ignore=True)

def get_recent_alerts(limit=10):
    db = get_connection()
    if "alerts" in db.table_names():
        return list(db.query(f"SELECT * FROM alerts ORDER BY id DESC LIMIT {limit}"))
    return []

"""Database Service: SQLite database initialization, migrations,
report storage, KPI aggregations, and simulated scenario injections.
"""
import sqlite_utils
import bcrypt
from datetime import datetime
from typing import List, Dict, Any, Tuple
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
    
    # Reports table
    if "reports" not in db.table_names():
        db["reports"].create({
            "id": int,
            "input_text": str,
            "verdict": str,
            "credibility_score": int,
            "risk_score": int,
            "location": str,
            "timestamp": str,
            "source_type": str,
            "physical_severity": int,
            "misinformation_risk": int,
            "is_simulated": int
        }, pk="id")
    else:
        # Schema migrations for backward compatibility
        existing_cols = db["reports"].columns_dict
        if "location" not in existing_cols:
            db["reports"].add_column("location", str)
        if "physical_severity" not in existing_cols:
            db["reports"].add_column("physical_severity", int)
        if "misinformation_risk" not in existing_cols:
            db["reports"].add_column("misinformation_risk", int)
        if "is_simulated" not in existing_cols:
            db["reports"].add_column("is_simulated", int)
        
    # Logs table
    if "logs" not in db.table_names():
        db["logs"].create({
            "id": int,
            "event": str,
            "timestamp": str
        }, pk="id")
        
    # Alerts table for GNews API
    if "alerts" not in db.table_names():
        db["alerts"].create({
            "id": int,
            "title": str,
            "description": str,
            "source": str,
            "publishedAt": str,
            "url": str,
            "location": str,
            "fetched_at": str,
            "is_simulated": int
        }, pk="id")
    else:
        if "is_simulated" not in db["alerts"].columns_dict:
            db["alerts"].add_column("is_simulated", int)
        
    seed_users()
    seed_demo_reports()

def seed_users():
    db = get_connection()
    users = db["users"]
    
    if users.count == 0:
        user_hash = bcrypt.hashpw(b"user123", bcrypt.gensalt()).decode('utf-8')
        admin_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
        users.insert_all([
            {"username": "user", "password": user_hash, "role": "user"},
            {"username": "admin", "password": admin_hash, "role": "authority"}
        ], ignore=True)

def seed_demo_reports():
    db = get_connection()
    reports = db["reports"]
    
    # Only seed if empty to provide initial map and dashboard data
    if reports.count == 0:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        reports.insert_all([
            {
                "input_text": "[SIMULATED] Flood rumor in Pimpri Chinchwad, evacuate now!",
                "verdict": "CONTRADICTED",
                "credibility_score": 15,
                "risk_score": 88,
                "location": "Pimpri Chinchwad",
                "timestamp": timestamp,
                "source_type": "text",
                "physical_severity": 65,
                "misinformation_risk": 92,
                "is_simulated": 1
            },
            {
                "input_text": "[SIMULATED] Massive industrial fire reported near Pune station.",
                "verdict": "SUPPORTED",
                "credibility_score": 90,
                "risk_score": 75,
                "location": "Pune",
                "timestamp": timestamp,
                "source_type": "image",
                "physical_severity": 78,
                "misinformation_risk": 15,
                "is_simulated": 1
            },
            {
                "input_text": "[SIMULATED] Road collapse warning issued in Mumbai by traffic police.",
                "verdict": "UNVERIFIED",
                "credibility_score": 50,
                "risk_score": 62,
                "location": "Mumbai",
                "timestamp": timestamp,
                "source_type": "text",
                "physical_severity": 70,
                "misinformation_risk": 55,
                "is_simulated": 1
            }
        ])

def force_seed_demo_reports():
    db = get_connection()
    reports = db["reports"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reports.insert_all([
        {
            "input_text": "[SIMULATED] Urgent flood evacuation triggered in Pimpri Chinchwad!",
            "verdict": "CONTRADICTED",
            "credibility_score": 10,
            "risk_score": 92,
            "location": "Pimpri Chinchwad",
            "timestamp": timestamp,
            "source_type": "text",
            "physical_severity": 65,
            "misinformation_risk": 95,
            "is_simulated": 1
        },
        {
            "input_text": "[SIMULATED] Massive industrial fire reported near Pune station.",
            "verdict": "SUPPORTED",
            "credibility_score": 92,
            "risk_score": 80,
            "location": "Pune",
            "timestamp": timestamp,
            "source_type": "image",
            "physical_severity": 82,
            "misinformation_risk": 12,
            "is_simulated": 1
        },
        {
            "input_text": "[SIMULATED] Traffic police warn of bridge collapse in Mumbai.",
            "verdict": "UNVERIFIED",
            "credibility_score": 48,
            "risk_score": 64,
            "location": "Mumbai",
            "timestamp": timestamp,
            "source_type": "text",
            "physical_severity": 75,
            "misinformation_risk": 58,
            "is_simulated": 1
        }
    ])

def save_report(
    input_text: str,
    verdict: str,
    credibility_score: int,
    risk_score: int,
    source_type: str = "text",
    location: str = "Unknown",
    physical_severity: int = 50,
    misinformation_risk: int = 50,
    is_simulated: int = 0
):
    db = get_connection()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db["reports"].insert({
        "input_text": input_text,
        "verdict": verdict,
        "credibility_score": credibility_score,
        "risk_score": risk_score,
        "location": location,
        "timestamp": timestamp,
        "source_type": source_type,
        "physical_severity": physical_severity,
        "misinformation_risk": misinformation_risk,
        "is_simulated": is_simulated
    })

def get_recent_reports(limit=5):
    db = get_connection()
    return list(db.query(f"SELECT * FROM reports ORDER BY id DESC LIMIT {limit}"))

def get_kpi_metrics() -> Tuple[int, int, int, int]:
    db = get_connection()
    today = datetime.now().strftime("%Y-%m-%d")
    total_today = list(db.query(f"SELECT COUNT(*) as count FROM reports WHERE timestamp LIKE '{today}%'"))[0]['count']
    high_risk = list(db.query("SELECT COUNT(*) as count FROM reports WHERE risk_score > 70"))[0]['count']
    # Match both cautious CONTRADICTED and legacy FAKE
    fake_claims = list(db.query("SELECT COUNT(*) as count FROM reports WHERE LOWER(verdict) IN ('fake', 'contradicted')"))[0]['count']
    hotspots = list(db.query("SELECT COUNT(DISTINCT location) as count FROM reports WHERE location IS NOT NULL AND location != 'Unknown' AND location != ''"))[0]['count']
    
    return total_today, high_risk, fake_claims, hotspots

def get_live_feed(limit=10):
    db = get_connection()
    return list(db.query(f"SELECT * FROM reports ORDER BY id DESC LIMIT {limit}"))

def get_priority_incidents(limit=10):
    db = get_connection()
    return list(db.query(f"SELECT * FROM reports ORDER BY risk_score DESC, timestamp DESC LIMIT {limit}"))

def get_unverified_queue():
    db = get_connection()
    return list(db.query("SELECT * FROM reports WHERE LOWER(verdict) IN ('unverified', 'needs verification', 'conflicting') OR credibility_score < 40 ORDER BY id DESC"))

def inject_scenario(scenario_type: str):
    db = get_connection()
    reports = db["reports"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if scenario_type == "Flood Rumor":
        reports.insert({
            "input_text": "[SIMULATED SCENARIO] Urgent flood evacuation triggered in Pimpri Chinchwad!",
            "verdict": "CONTRADICTED",
            "credibility_score": 12,
            "risk_score": 90,
            "location": "Pimpri Chinchwad",
            "timestamp": timestamp,
            "source_type": "text",
            "physical_severity": 65,
            "misinformation_risk": 94,
            "is_simulated": 1
        })
    elif scenario_type == "Fire Incident":
        reports.insert({
            "input_text": "[SIMULATED SCENARIO] Massive industrial fire reported near Pune station.",
            "verdict": "SUPPORTED",
            "credibility_score": 94,
            "risk_score": 82,
            "location": "Pune",
            "timestamp": timestamp,
            "source_type": "image",
            "physical_severity": 85,
            "misinformation_risk": 15,
            "is_simulated": 1
        })
    elif scenario_type == "Collapse Warning":
        reports.insert({
            "input_text": "[SIMULATED SCENARIO] Traffic police warn of bridge collapse in Mumbai.",
            "verdict": "UNVERIFIED",
            "credibility_score": 50,
            "risk_score": 65,
            "location": "Mumbai",
            "timestamp": timestamp,
            "source_type": "text",
            "physical_severity": 75,
            "misinformation_risk": 60,
            "is_simulated": 1
        })

def get_all_reports():
    db = get_connection()
    return list(db.query("SELECT * FROM reports"))

def save_alerts(alerts_list: List[Dict[str, Any]]):
    if not alerts_list:
        return
    db = get_connection()
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = []
    for alert in alerts_list:
        formatted.append({
            "title": alert.get("title", ""),
            "description": alert.get("description", ""),
            "source": alert.get("source", ""),
            "publishedAt": alert.get("publishedAt", ""),
            "url": alert.get("url", ""),
            "location": alert.get("location", "India"),
            "fetched_at": fetched_at,
            "is_simulated": 1 if alert.get("is_simulated", False) else 0
        })
        
    db["alerts"].insert_all(formatted, ignore=True)

def get_recent_alerts(limit=10):
    db = get_connection()
    if "alerts" in db.table_names():
        return list(db.query(f"SELECT * FROM alerts ORDER BY id DESC LIMIT {limit}"))
    return []

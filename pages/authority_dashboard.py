import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from components.layout import page_wrapper
from components.cards import metric_card
from components.alerts import live_alert_card
from components.charts import plot_risk_distribution, plot_verdict_breakdown, plot_top_locations
from components.map import render_crisis_map
from services.auth import get_role, is_logged_in
from services.db import get_kpi_metrics, get_live_feed, get_priority_incidents, get_unverified_queue, get_all_reports, get_recent_alerts, force_seed_demo_reports, get_recent_reports
from services.gnews import fetch_live_alerts
from services.langfuse_client import is_available as langfuse_available, fetch_recent_traces
from agents.orchestrator import get_last_trace_metadata

# Auto-refresh every 300 seconds (5 mins) for API feeds
@st.cache_data(ttl=300)
def get_live_apis():
    alerts = fetch_live_alerts(limit=5)
    return alerts

# Keep DB reports refresh tighter
@st.cache_data(ttl=60)
def fetch_all_reports_cached():
    return get_all_reports()

def render():
    if not is_logged_in() or get_role() != "authority":
        st.warning("Unauthorized. Please log in as an Authority.")
        return
        
    page_wrapper("Authority Command Center")
    st.markdown("#### Real-Time Crisis Intelligence Dashboard")
    
    # Top Controls (Refresh & Scenario Simulator)
    col_demo, col_blank, col_btn = st.columns([3, 5, 2])
    with col_demo:
        scenario = st.selectbox("Scenario Simulator", ["None", "Flood Rumor", "Fire Incident", "Collapse Warning"], label_visibility="collapsed")
        if scenario != "None" and st.button(f"Inject {scenario}"):
            with st.spinner("Injecting scenario..."):
                from services.db import inject_scenario
                inject_scenario(scenario)
                fetch_all_reports_cached.clear()
                st.success(f"{scenario} injected!")
                st.rerun()
                    
    with col_btn:
        if st.button("🔄 Refresh Feeds", use_container_width=True):
            get_live_apis.clear()
            fetch_all_reports_cached.clear()
            st.rerun()

    # Fetch dynamic APIs
    with st.spinner("Syncing global intelligence feeds..."):
        try:
            gnews_alerts = get_live_apis()
        except Exception:
            gnews_alerts = []

    # SECTION 3: KPI Cards (Combined Metrics)
    try:
        total_reports, high_risk, fake_claims, active_hotspots = get_kpi_metrics()
        # Dynamically inflate total tracking based on system alerts
        db_alerts = get_recent_alerts(100)
        total_system_tracked = total_reports + len(db_alerts)
    except Exception as e:
        total_system_tracked, high_risk, fake_claims, active_hotspots = 0, 0, 0, 0
        st.error("Could not load KPI metrics.")
        
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        metric_card("Total Events Tracked", str(total_system_tracked))
    with kpi2:
        metric_card("High Risk User Reports", str(high_risk))
    with kpi3:
        metric_card("Fake Claims Detected", str(fake_claims))
    with kpi4:
        metric_card("Active Hotspots", str(active_hotspots))
        
    st.markdown("---")
    
    # Action Center
    if active_hotspots > 0:
        try:
            all_reports_df = pd.DataFrame(fetch_all_reports_cached())
            top_loc = all_reports_df[all_reports_df['location'].notna() & (all_reports_df['location'] != "Unknown")]['location'].mode()[0]
            st.error(f"🚨 **COMMAND ACTION CENTER | Top Risk Zone:** {top_loc.upper()} | **Recommended Action:** Escalate local verification teams to {top_loc} immediately.")
        except:
            pass
    
    # Main Dashboard Body
    col_main, col_feed = st.columns([7, 3])
    
    with col_main:
        # Fetch all data for map and filters
        all_reports = fetch_all_reports_cached()
        df_all = pd.DataFrame(all_reports) if all_reports else pd.DataFrame()
        
        # SECTION: Map Filters
        st.markdown("##### 🗺️ Map Filters")
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            city_filter = st.selectbox("City", ["All", "Pune", "Pimpri Chinchwad", "Mumbai", "Delhi", "Nagpur", "Unknown"], label_visibility="collapsed")
        with fcol2:
            risk_filter = st.selectbox("Risk Level", ["All", "High Only (>70)"], label_visibility="collapsed")
        with fcol3:
            time_filter = st.selectbox("Timeframe", ["All", "Today", "Last 1h"], label_visibility="collapsed")
            
        # Apply Filters
        filtered_df = df_all.copy()
        if not filtered_df.empty:
            if city_filter != "All":
                filtered_df = filtered_df[filtered_df['location'].str.contains(city_filter, case=False, na=False)]
            
            if risk_filter == "High Only (>70)":
                filtered_df = filtered_df[filtered_df['risk_score'] > 70]
                
            if time_filter == "Today":
                today = datetime.now().strftime("%Y-%m-%d")
                filtered_df = filtered_df[filtered_df['timestamp'].str.startswith(today)]
            elif time_filter == "Last 1h":
                one_hour_ago = datetime.now() - timedelta(hours=1)
                filtered_df['parsed_time'] = pd.to_datetime(filtered_df['timestamp'])
                filtered_df = filtered_df[filtered_df['parsed_time'] >= one_hour_ago]
                
        # MAP SECTION
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            render_crisis_map(filtered_df)
        except Exception as e:
            st.error(f"Map rendering failed: {e}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # SECTION 5: Priority Alerts Table
        st.markdown("### 🚨 Priority Local Incidents")
        try:
            priority_data = get_priority_incidents(limit=5)
            if priority_data:
                df_priority = pd.DataFrame(priority_data)
                df_p_show = df_priority[['input_text', 'location', 'verdict', 'risk_score', 'timestamp']]
                df_p_show.columns = ['Message', 'Location', 'Verdict', 'Risk', 'Time']
                df_p_show['Message'] = df_p_show['Message'].apply(lambda x: x[:40] + "..." if len(x)>40 else x)
                st.dataframe(df_p_show, use_container_width=True, hide_index=True)
            else:
                st.info("No priority incidents at this time.")
        except Exception:
            st.error("Failed to load priority incidents.")
            
        st.markdown("---")
        
        # SECTION 6: Quick Analytics Charts
        st.markdown("### 📊 Local Intelligence Analytics")
        if not df_all.empty:
            chart_col1, chart_col2, chart_col3 = st.columns(3)
            with chart_col1:
                try:
                    plot_risk_distribution(df_all)
                except: st.error("Chart Error")
            with chart_col2:
                try:
                    plot_verdict_breakdown(df_all)
                except: st.error("Chart Error")
            with chart_col3:
                try:
                    plot_top_locations(df_all)
                except: st.error("Chart Error")
        else:
            st.info("Not enough data to generate charts.")
            
        st.markdown("---")
        
        # SECTION 8: Verification Queue
        st.markdown("### 🔍 Verification Queue")
        try:
            unverified_data = get_unverified_queue()
            if unverified_data:
                df_unv = pd.DataFrame(unverified_data)
                
                # Add a reason column
                def get_reason(row):
                    if str(row['verdict']).upper() == 'UNVERIFIED':
                        return "Needs Review"
                    if row['credibility_score'] < 40:
                        return "Low Confidence"
                    return "System Flagged"
                
                df_unv['Reason'] = df_unv.apply(get_reason, axis=1)
                
                df_unv_show = df_unv[['timestamp', 'input_text', 'location', 'risk_score', 'Reason']]
                df_unv_show.columns = ['Time', 'Message', 'Location', 'Risk', 'Reason']
                df_unv_show['Message'] = df_unv_show['Message'].apply(lambda x: x[:40] + "..." if len(x)>40 else x)
                st.dataframe(df_unv_show, use_container_width=True, hide_index=True)
            else:
                st.success("Verification queue is empty.")
        except Exception:
            st.error("Failed to load queue.")

    with col_feed:
        # SECTION: Global Live Crisis Alerts (GNews)
        st.markdown("### 🌐 Live Crisis Alerts")
        if gnews_alerts:
            for alert in gnews_alerts:
                try:
                    dt = datetime.fromisoformat(alert['publishedAt'].replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M")
                except:
                    time_str = "Recent"
                    
                st.markdown(f"""
                <div style='padding: 10px; border-left: 3px solid #dc3545; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 4px; margin-bottom: 10px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
                        <span style='color: #dc3545; font-size: 10px; font-weight: bold; padding: 2px 6px; border: 1px solid #dc3545; border-radius: 10px;'>ALERT</span>
                        <span style='color: #6e7589; font-size: 11px;'>{time_str} | {alert['source'][:15]}</span>
                    </div>
                    <a href='{alert['url']}' target='_blank' style='color: #0068c9; text-decoration: none; font-size: 14px; font-weight: 500;'>{alert['title']}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Live news temporarily unavailable. Using cached alerts.")
            
        st.markdown("---")
            
        # SECTION: Community Reports Feed (Local Database)
        st.markdown("### 👥 Community Reports Feed")
        try:
            recent_reports = get_recent_reports(limit=5)
            if recent_reports:
                for rep in recent_reports:
                    color = "#28a745" if rep['risk_score'] < 40 else ("#ffc107" if rep['risk_score'] < 70 else "#dc3545")
                    st.markdown(f"""
                    <div style='padding: 10px; border-left: 3px solid {color}; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 4px; margin-bottom: 10px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
                            <span style='color: {color}; font-size: 10px; font-weight: bold;'>{rep['location']}</span>
                            <span style='color: #6e7589; font-size: 11px;'>Score: {rep['risk_score']}</span>
                        </div>
                        <div style='color: #31333f; font-size: 13px;'>{rep['input_text'][:100] + ('...' if len(rep['input_text']) > 100 else '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No community reports available.")
        except Exception as e:
            st.error(f"Could not load community reports.")

    # ============================================================
    # AI TRACE TAB — Langfuse Observability Panel
    # ============================================================
    st.markdown("---")
    st.markdown("### 🧠 AI Trace — Agent Observability")
    
    if not langfuse_available():
        st.info("Tracing currently unavailable. Langfuse keys not configured.")
    else:
        trace_meta = get_last_trace_metadata()
        
        if trace_meta:
            # Header row with query and timestamp
            tc1, tc2 = st.columns([6, 4])
            with tc1:
                st.markdown(f"""
                <div style='padding: 15px; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 8px; border-left: 4px solid #0068c9;'>
                    <p style='color: #6e7589; margin: 0; font-size: 12px;'>Latest Query</p>
                    <p style='color: #31333f; margin: 4px 0 0 0; font-size: 18px; font-weight: 600;'>{trace_meta.get('query', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            with tc2:
                st.markdown(f"""
                <div style='padding: 15px; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 8px; border-left: 4px solid #0068c9;'>
                    <p style='color: #6e7589; margin: 0; font-size: 12px;'>Response Time | Timestamp</p>
                    <p style='color: #31333f; margin: 4px 0 0 0; font-size: 18px; font-weight: 600;'>{trace_meta.get('response_time', 'N/A')} | {trace_meta.get('timestamp', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Agent execution status
            st.markdown("##### Agent Execution Pipeline")
            agent_cols = st.columns(5)
            agent_names = ["ExtractionAgent", "VerificationAgent", "RiskAgent", "ActionAgent", "SummaryAgent"]
            agent_icons = ["🔍", "✅", "⚠️", "🎯", "📝"]
            agents_data = trace_meta.get("agents", {})
            
            for i, (name, icon) in enumerate(zip(agent_names, agent_icons)):
                with agent_cols[i]:
                    status = agents_data.get(name, "pending")
                    color = "#28a745" if status == "completed" else "#ffc107"
                    check = "Done" if status == "completed" else "..."
                    st.markdown(f"""
                    <div style='text-align: center; padding: 12px; background: #ffffff; border-radius: 8px; border: 1px solid {color}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                        <div style='font-size: 24px;'>{icon}</div>
                        <div style='color: #31333f; font-size: 12px; font-weight: 600; margin-top: 4px;'>{name.replace('Agent', '')}</div>
                        <div style='color: {color}; font-size: 11px; margin-top: 2px;'>{check}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Result summary
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                st.markdown(f"""
                <div style='padding: 12px; background: #f0f2f6; border-radius: 8px; text-align: center; border: 1px solid #e6e9ef;'>
                    <p style='color: #6e7589; margin: 0; font-size: 11px;'>Final Verdict</p>
                    <p style='color: #31333f; margin: 4px 0 0 0; font-size: 16px; font-weight: bold;'>{trace_meta.get('verdict', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            with r2:
                st.markdown(f"""
                <div style='padding: 12px; background: #f0f2f6; border-radius: 8px; text-align: center; border: 1px solid #e6e9ef;'>
                    <p style='color: #6e7589; margin: 0; font-size: 11px;'>Credibility</p>
                    <p style='color: #31333f; margin: 4px 0 0 0; font-size: 16px; font-weight: bold;'>{trace_meta.get('credibility', 'N/A')}%</p>
                </div>
                """, unsafe_allow_html=True)
            with r3:
                st.markdown(f"""
                <div style='padding: 12px; background: #f0f2f6; border-radius: 8px; text-align: center; border: 1px solid #e6e9ef;'>
                    <p style='color: #6e7589; margin: 0; font-size: 11px;'>Location</p>
                    <p style='color: #31333f; margin: 4px 0 0 0; font-size: 16px; font-weight: bold;'>{trace_meta.get('location', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            with r4:
                st.markdown(f"""
                <div style='padding: 12px; background: #f0f2f6; border-radius: 8px; text-align: center; border: 1px solid #e6e9ef;'>
                    <p style='color: #6e7589; margin: 0; font-size: 11px;'>Trace ID</p>
                    <p style='color: #0068c9; margin: 4px 0 0 0; font-size: 12px; font-family: monospace;'>{str(trace_meta.get('trace_id', 'N/A'))[:16]}...</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Langfuse dashboard link
            st.markdown("<br>", unsafe_allow_html=True)
            langfuse_host = os.getenv("LANGFUSE_BASE_URL", os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com"))
            st.link_button("Open Full Langfuse Dashboard", langfuse_host, use_container_width=True)
            
        else:
            st.info("No traces recorded yet. Submit a verification query from the User Dashboard to generate a trace.")
        
        # Recent traces table
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("##### Recent Traces")
        try:
            recent_traces = fetch_recent_traces(limit=5)
            if recent_traces:
                trace_rows = []
                for t in recent_traces:
                    trace_rows.append({
                        "Timestamp": t.get("timestamp", "")[:19],
                        "Query": str(t.get("input", {}).get("claim", "N/A"))[:50],
                        "Verdict": str(t.get("output", {}).get("verdict", "N/A")),
                        "Credibility": str(t.get("output", {}).get("credibility", "N/A")),
                        "Response Time": str(t.get("output", {}).get("response_time_seconds", "N/A")) + "s",
                    })
                st.dataframe(pd.DataFrame(trace_rows), use_container_width=True, hide_index=True)
            else:
                st.info("No traces available from Langfuse yet.")
        except Exception as e:
            st.warning(f"Could not fetch traces from Langfuse: {e}")

if __name__ == "__main__":
    render()

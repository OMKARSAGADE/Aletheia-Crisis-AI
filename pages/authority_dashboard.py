"""Authority Command Center: Real-time crisis intelligence dashboard,
geospatial hotspot tracking, triage verification queue, and agent observability.
"""
import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from components.layout import page_wrapper
from components.cards import metric_card
from components.charts import plot_risk_distribution, plot_verdict_breakdown, plot_top_locations
from components.map import render_crisis_map
from services.auth import get_role, is_logged_in
from services.db import (
    get_kpi_metrics, get_priority_incidents, get_unverified_queue,
    get_all_reports, get_recent_alerts, inject_scenario, get_recent_reports
)
from services.gnews import fetch_live_alerts, is_demo_mode, get_gnews_api_key
from services.langfuse_client import is_available as langfuse_available, fetch_recent_traces
from agents.orchestrator import get_last_trace_metadata

@st.cache_data(ttl=120)
def get_live_apis():
    return fetch_live_alerts(limit=6)

@st.cache_data(ttl=30)
def fetch_all_reports_cached():
    return get_all_reports()

def render():
    if not is_logged_in() or get_role() != "authority":
        st.warning("Unauthorized. Please log in as an Authority.")
        return
        
    page_wrapper("Authority Command Center")
    st.markdown("#### Real-Time Crisis Intelligence & Threat Triage Dashboard")
    st.caption("Coordinate disaster response, monitor geographic clusters, and combat viral misinformation.")
    
    # Check if simulation/demo mode is active
    api_key_set = bool(get_gnews_api_key())
    if not api_key_set or is_demo_mode():
        st.warning("⚠️ **System Notice (Demo Mode Active):** Live news APIs are running with simulated crisis scenarios. External data is labeled as simulated.")

    # Top Controls
    col_demo, col_blank, col_btn = st.columns([4, 4, 2])
    with col_demo:
        scenario = st.selectbox(
            "Inject Simulated Crisis Scenario",
            ["None", "Flood Rumor", "Fire Incident", "Collapse Warning"],
            label_visibility="collapsed"
        )
        if scenario != "None" and st.button(f"Inject {scenario} Scenario"):
            with st.spinner("Injecting test scenario into local registry..."):
                inject_scenario(scenario)
                fetch_all_reports_cached.clear()
                st.success(f"Simulated {scenario} registered successfully!")
                st.rerun()
                    
    with col_btn:
        if st.button("🔄 Refresh Data", use_container_width=True):
            get_live_apis.clear()
            fetch_all_reports_cached.clear()
            st.rerun()

    # Sync News Feeds
    try:
        gnews_alerts = get_live_apis()
    except Exception:
        gnews_alerts = []

    # KPI Metrics
    try:
        total_reports, high_risk, fake_claims, active_hotspots = get_kpi_metrics()
        db_alerts = get_recent_alerts(100)
        total_system_tracked = total_reports + len(db_alerts)
    except Exception as e:
        total_system_tracked, high_risk, fake_claims, active_hotspots = 0, 0, 0, 0
        st.error("Could not load KPI metrics.")
        
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        metric_card("Total Tracked Events", str(total_system_tracked), "Verified & Monitored")
    with kpi2:
        metric_card("High Priority Incidents", str(high_risk), "Priority Score > 70")
    with kpi3:
        metric_card("Debunked Misinfo", str(fake_claims), "Contradicted Rumors")
    with kpi4:
        metric_card("Active Geo Hotspots", str(active_hotspots), "Unique Municipal Sectors")
        
    st.markdown("---")
    
    # Dynamic Command Action Alert
    all_reports = fetch_all_reports_cached()
    df_all = pd.DataFrame(all_reports) if all_reports else pd.DataFrame()

    if not df_all.empty and 'location' in df_all.columns:
        valid_locs = df_all[df_all['location'].notna() & (df_all['location'] != "Unknown") & (df_all['location'] != "")]
        if not valid_locs.empty:
            top_loc = valid_locs['location'].mode()[0]
            top_incidents = valid_locs[valid_locs['location'] == top_loc]
            avg_risk = int(top_incidents['risk_score'].mean()) if 'risk_score' in top_incidents.columns else 60
            
            st.error(
                f"🚨 **COMMAND ACTION CENTER | Priority Sector:** **{top_loc.upper()}** (Avg Risk: {avg_risk}/100) | "
                f"**Directive:** Deploy ground field monitors and release verified municipal bulletin to prevent panic."
            )
    
    col_main, col_feed = st.columns([7, 3])
    
    with col_main:
        st.markdown("##### 🗺️ Geospatial Intelligence Map & Filters")
        fcol1, fcol2, fcol3 = st.columns(3)
        with fcol1:
            city_filter = st.selectbox("Filter City", ["All", "Pune", "Pimpri Chinchwad", "Mumbai", "Delhi", "Nagpur", "Assam"], label_visibility="collapsed")
        with fcol2:
            risk_filter = st.selectbox("Risk Filter", ["All Priority Levels", "High Priority Only (>70)", "Medium & High (>40)"], label_visibility="collapsed")
        with fcol3:
            time_filter = st.selectbox("Timeframe", ["All Time", "Today Only", "Last 1 Hour"], label_visibility="collapsed")
            
        filtered_df = df_all.copy()
        if not filtered_df.empty:
            if city_filter != "All" and 'location' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['location'].str.contains(city_filter, case=False, na=False)]
            
            if risk_filter == "High Priority Only (>70)" and 'risk_score' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['risk_score'] > 70]
            elif risk_filter == "Medium & High (>40)" and 'risk_score' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['risk_score'] > 40]
                
            if time_filter == "Today Only" and 'timestamp' in filtered_df.columns:
                today = datetime.now().strftime("%Y-%m-%d")
                filtered_df = filtered_df[filtered_df['timestamp'].str.startswith(today)]
            elif time_filter == "Last 1 Hour" and 'timestamp' in filtered_df.columns:
                one_hour_ago = datetime.now() - timedelta(hours=1)
                try:
                    filtered_df['parsed_time'] = pd.to_datetime(filtered_df['timestamp'])
                    filtered_df = filtered_df[filtered_df['parsed_time'] >= one_hour_ago]
                except Exception:
                    pass
                
        # Interactive Crisis Map
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            render_crisis_map(filtered_df)
        except Exception as e:
            st.error(f"Map rendering error: {e}")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Priority Incidents Table
        st.markdown("### 🚨 Priority Local Incidents")
        try:
            priority_data = get_priority_incidents(limit=5)
            if priority_data:
                df_priority = pd.DataFrame(priority_data)
                cols = ['input_text', 'location', 'verdict', 'risk_score', 'timestamp']
                show_cols = [c for c in cols if c in df_priority.columns]
                df_p_show = df_priority[show_cols].copy()
                df_p_show.rename(columns={
                    'input_text': 'Incident Claim',
                    'location': 'Location',
                    'verdict': 'Status',
                    'risk_score': 'Priority Score',
                    'timestamp': 'Time'
                }, inplace=True)
                df_p_show['Incident Claim'] = df_p_show['Incident Claim'].apply(lambda x: str(x)[:45] + "..." if len(str(x))>45 else str(x))
                st.dataframe(df_p_show, use_container_width=True, hide_index=True)
            else:
                st.info("No priority incidents at this time.")
        except Exception:
            st.error("Failed to load priority incidents.")
            
        st.markdown("---")
        
        # Analytics Charts
        st.markdown("### 📊 Crisis Intelligence Analytics")
        if not df_all.empty:
            chart_col1, chart_col2, chart_col3 = st.columns(3)
            with chart_col1:
                try:
                    plot_risk_distribution(df_all)
                except Exception:
                    st.error("Chart Error")
            with chart_col2:
                try:
                    plot_verdict_breakdown(df_all)
                except Exception:
                    st.error("Chart Error")
            with chart_col3:
                try:
                    plot_top_locations(df_all)
                except Exception:
                    st.error("Chart Error")
        else:
            st.info("Insufficient data to plot analytics.")
            
        st.markdown("---")
        
        # Verification Queue
        st.markdown("### 🔍 Verification Triage Queue")
        try:
            unverified_data = get_unverified_queue()
            if unverified_data:
                df_unv = pd.DataFrame(unverified_data)
                
                def get_triage_reason(row):
                    v = str(row.get('verdict', '')).upper()
                    if v in ['UNVERIFIED', 'NEEDS VERIFICATION']:
                        return "Awaiting Corroboration"
                    if v == 'CONFLICTING':
                        return "Conflicting Reports"
                    if row.get('credibility_score', 50) < 40:
                        return "Low Credibility / High Risk"
                    return "System Review"
                
                df_unv['Triage Reason'] = df_unv.apply(get_triage_reason, axis=1)
                cols_unv = ['timestamp', 'input_text', 'location', 'risk_score', 'Triage Reason']
                show_u = [c for c in cols_unv if c in df_unv.columns]
                df_unv_show = df_unv[show_u].copy()
                df_unv_show.rename(columns={
                    'timestamp': 'Reported Time',
                    'input_text': 'Claim Text',
                    'location': 'Location',
                    'risk_score': 'Priority'
                }, inplace=True)
                df_unv_show['Claim Text'] = df_unv_show['Claim Text'].apply(lambda x: str(x)[:45] + "..." if len(str(x))>45 else str(x))
                st.dataframe(df_unv_show, use_container_width=True, hide_index=True)
            else:
                st.success("Verification queue clear. No unverified high-priority claims pending.")
        except Exception:
            st.error("Failed to load triage queue.")

    with col_feed:
        st.markdown("### 🌐 Monitored Intelligence Feeds")
        if gnews_alerts:
            for alert in gnews_alerts:
                time_str = "Recent"
                try:
                    dt = datetime.fromisoformat(alert['publishedAt'].replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M")
                except Exception:
                    pass
                    
                is_sim = alert.get('is_simulated', False)
                border_color = "#d97706" if is_sim else "#dc3545"
                tag_label = "SIMULATED" if is_sim else "LIVE ALERT"
                tag_color = "#d97706" if is_sim else "#dc3545"
                
                st.markdown(f"""
                <div style='padding: 10px; border-left: 3px solid {border_color}; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 4px; margin-bottom: 10px;'>
                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
                        <span style='color: {tag_color}; font-size: 10px; font-weight: bold; padding: 2px 6px; border: 1px solid {tag_color}; border-radius: 10px;'>{tag_label}</span>
                        <span style='color: #6e7589; font-size: 11px;'>{time_str} | {str(alert.get('source', 'Unknown'))[:14]}</span>
                    </div>
                    <a href='{alert.get('url', '#')}' target='_blank' style='color: #0068c9; text-decoration: none; font-size: 13px; font-weight: 500;'>{alert.get('title', '')}</a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("News intelligence feed idle.")
            
        st.markdown("---")
            
        st.markdown("### 👥 Community Reports Feed")
        try:
            recent_reports = get_recent_reports(limit=6)
            if recent_reports:
                for rep in recent_reports:
                    r_score = rep.get('risk_score', 50)
                    color = "#28a745" if r_score < 40 else ("#ffc107" if r_score < 70 else "#dc3545")
                    loc_name = rep.get('location') or "Unknown"
                    is_sim = rep.get('is_simulated', 0) == 1
                    sim_badge = " <span style='color: #d97706; font-size: 9px;'>[SIM]</span>" if is_sim else ""
                    st.markdown(f"""
                    <div style='padding: 10px; border-left: 3px solid {color}; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 4px; margin-bottom: 10px;'>
                        <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;'>
                            <span style='color: {color}; font-size: 11px; font-weight: bold;'>{loc_name}{sim_badge}</span>
                            <span style='color: #6e7589; font-size: 11px;'>Priority: {r_score}</span>
                        </div>
                        <div style='color: #31333f; font-size: 13px;'>{str(rep.get('input_text',''))[:90] + ('...' if len(str(rep.get('input_text',''))) > 90 else '')}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No community reports recorded.")
        except Exception:
            st.error("Could not load community feed.")

    # Agent Observability (Langfuse Trace Panel)
    st.markdown("---")
    st.markdown("### 🧠 AI Trace & Multi-Agent Observability")
    
    if not langfuse_available():
        st.info("ℹ️ Agent execution traces active in local memory. (Configure LANGFUSE_PUBLIC_KEY & LANGFUSE_SECRET_KEY in `.env` for cloud analytics).")
    
    trace_meta = get_last_trace_metadata()
    if trace_meta:
        tc1, tc2 = st.columns([6, 4])
        with tc1:
            st.markdown(f"""
            <div style='padding: 15px; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 8px; border-left: 4px solid #0068c9;'>
                <p style='color: #6e7589; margin: 0; font-size: 12px;'>Latest Orchestrated Query</p>
                <p style='color: #31333f; margin: 4px 0 0 0; font-size: 16px; font-weight: 600;'>{trace_meta.get('query', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        with tc2:
            st.markdown(f"""
            <div style='padding: 15px; background: #ffffff; border: 1px solid #e6e9ef; border-radius: 8px; border-left: 4px solid #0068c9;'>
                <p style='color: #6e7589; margin: 0; font-size: 12px;'>Pipeline Duration | Timestamp</p>
                <p style='color: #31333f; margin: 4px 0 0 0; font-size: 16px; font-weight: 600;'>{trace_meta.get('response_time', 'N/A')} | {trace_meta.get('timestamp', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Agent execution pipeline cards
        st.markdown("##### Agent Pipeline State")
        agent_cols = st.columns(5)
        agent_names = ["ExtractionAgent", "VerificationAgent", "RiskAgent", "ActionAgent", "SummaryAgent"]
        agent_icons = ["🔍", "✅", "⚠️", "🎯", "📝"]
        agents_data = trace_meta.get("agents", {})
        
        for i, (name, icon) in enumerate(zip(agent_names, agent_icons)):
            with agent_cols[i]:
                status = agents_data.get(name, "completed")
                color = "#28a745" if status == "completed" else "#ffc107"
                check = "Done" if status == "completed" else "Pending"
                st.markdown(f"""
                <div style='text-align: center; padding: 12px; background: #ffffff; border-radius: 8px; border: 1px solid {color}; box-shadow: 0 1px 3px rgba(0,0,0,0.05);'>
                    <div style='font-size: 22px;'>{icon}</div>
                    <div style='color: #31333f; font-size: 12px; font-weight: 600; margin-top: 4px;'>{name.replace('Agent', '')}</div>
                    <div style='color: {color}; font-size: 11px; margin-top: 2px;'>{check}</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Result summary metrics
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(f"""
            <div style='padding: 12px; background: #f0f2f6; border-radius: 8px; text-align: center; border: 1px solid #e6e9ef;'>
                <p style='color: #6e7589; margin: 0; font-size: 11px;'>Verdict</p>
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
                <p style='color: #6e7589; margin: 0; font-size: 11px;'>Physical Severity</p>
                <p style='color: #31333f; margin: 4px 0 0 0; font-size: 16px; font-weight: bold;'>{trace_meta.get('physical_severity', 'N/A')}/100</p>
            </div>
            """, unsafe_allow_html=True)
        with r4:
            st.markdown(f"""
            <div style='padding: 12px; background: #f0f2f6; border-radius: 8px; text-align: center; border: 1px solid #e6e9ef;'>
                <p style='color: #6e7589; margin: 0; font-size: 11px;'>Misinfo Risk</p>
                <p style='color: #31333f; margin: 4px 0 0 0; font-size: 16px; font-weight: bold;'>{trace_meta.get('misinformation_risk', 'N/A')}/100</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Submit a claim verification from the Citizen Portal to observe live agent execution traces.")

if __name__ == "__main__":
    render()

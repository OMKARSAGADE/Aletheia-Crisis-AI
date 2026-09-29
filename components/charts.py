"""Plotly Chart Components for Crisis Analytics."""
import plotly.express as px
import pandas as pd
import streamlit as st

def plot_risk_distribution(df):
    if df.empty:
        st.info("No data available for Risk Distribution.")
        return
        
    bins = [0, 33, 66, 100]
    labels = ['Low Risk', 'Medium Risk', 'High Risk']
    df_copy = df.copy()
    df_copy['Risk Level'] = pd.cut(df_copy['risk_score'], bins=bins, labels=labels, include_lowest=True)
    
    counts = df_copy['Risk Level'].value_counts().reset_index()
    counts.columns = ['Risk Level', 'Count']
    
    color_map = {'Low Risk': '#28a745', 'Medium Risk': '#ffc107', 'High Risk': '#dc3545'}
    
    fig = px.pie(counts, values='Count', names='Risk Level', 
                 title="Operational Risk Distribution",
                 color='Risk Level',
                 color_discrete_map=color_map,
                 hole=0.45)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#31333f',
        margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_verdict_breakdown(df):
    if df.empty:
        st.info("No data available for Verdict Breakdown.")
        return
        
    df_copy = df.copy()
    # Normalize verdicts to standardized cautious taxonomy
    def normalize_verdict(v):
        v_str = str(v).upper()
        if "REAL" in v_str or "SUPPORTED" in v_str:
            return "SUPPORTED"
        if "FAKE" in v_str or "CONTRADICTED" in v_str:
            return "CONTRADICTED"
        if "CONFLICTING" in v_str:
            return "CONFLICTING"
        return "UNVERIFIED"

    df_copy['Verdict Category'] = df_copy['verdict'].apply(normalize_verdict)
    counts = df_copy['Verdict Category'].value_counts().reset_index()
    counts.columns = ['Verdict', 'Count']
    
    color_map = {
        'SUPPORTED': '#28a745',
        'CONTRADICTED': '#dc3545',
        'UNVERIFIED': '#ffc107',
        'CONFLICTING': '#6f42c1'
    }
    
    fig = px.bar(counts, x='Verdict', y='Count', 
                 title="Verification Status Breakdown",
                 color='Verdict',
                 color_discrete_map=color_map,
                 text='Count')
                 
    fig.update_traces(textfont_size=13, textposition="outside", cliponaxis=False)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#31333f',
        showlegend=False,
        margin=dict(t=40, b=10, l=10, r=10),
        xaxis_title=None,
        yaxis_title=None
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_top_locations(df):
    if df.empty:
        st.info("No data available for Top Locations.")
        return
        
    loc_df = df[df['location'].notna() & (df['location'] != "Unknown") & (df['location'] != "")].copy()
    if loc_df.empty:
        st.info("No valid location data available.")
        return
        
    counts = loc_df['location'].value_counts().head(5).reset_index()
    counts.columns = ['Location', 'Incident Count']
    
    fig = px.bar(counts, y='Location', x='Incident Count', orientation='h',
                 title="Top Geographic Hotspots",
                 color_discrete_sequence=['#0068c9'],
                 text='Incident Count')
                 
    fig.update_traces(textfont_size=13, textposition="outside", cliponaxis=False)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#31333f',
        yaxis={'categoryorder':'total ascending'},
        margin=dict(t=40, b=10, l=10, r=10),
        xaxis_title=None,
        yaxis_title=None
    )
    st.plotly_chart(fig, use_container_width=True)

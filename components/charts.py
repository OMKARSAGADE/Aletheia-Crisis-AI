import plotly.express as px
import pandas as pd
import streamlit as st

def plot_risk_distribution(df):
    if df.empty:
        st.info("No data available for Risk Distribution.")
        return
        
    
    bins = [0, 33, 66, 100]
    labels = ['Low', 'Medium', 'High']
    df['Risk Level'] = pd.cut(df['risk_score'], bins=bins, labels=labels, include_lowest=True)
    
    counts = df['Risk Level'].value_counts().reset_index()
    counts.columns = ['Risk Level', 'Count']
    
    color_map = {'Low': '#28a745', 'Medium': '#ffc107', 'High': '#dc3545'}
    
    fig = px.pie(counts, values='Count', names='Risk Level', 
                 title="Risk Distribution",
                 color='Risk Level',
                 color_discrete_map=color_map,
                 hole=0.5)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#fff',
        margin=dict(t=40, b=10, l=10, r=10),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_verdict_breakdown(df):
    if df.empty:
        st.info("No data available for Verdict Breakdown.")
        return
        
    counts = df['verdict'].value_counts().reset_index()
    counts.columns = ['Verdict', 'Count']
    
    color_map = {'REAL': '#28a745', 'FAKE': '#dc3545', 'UNVERIFIED': '#ffc107'}
    
    counts['Verdict'] = counts['Verdict'].str.upper()
    
    fig = px.bar(counts, x='Verdict', y='Count', 
                 title="Verdict Breakdown",
                 color='Verdict',
                 color_discrete_map=color_map,
                 text='Count')
                 
    fig.update_traces(textfont_size=14, textangle=0, textposition="outside", cliponaxis=False)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#fff',
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
        
    
    loc_df = df[df['location'].notna() & (df['location'] != "Unknown") & (df['location'] != "")]
    if loc_df.empty:
        st.info("No valid location data available.")
        return
        
    counts = loc_df['location'].value_counts().head(5).reset_index()
    counts.columns = ['Location', 'Incident Count']
    
    fig = px.bar(counts, y='Location', x='Incident Count', orientation='h',
                 title="Top Mentioned Locations",
                 color_discrete_sequence=['#007acc'],
                 text='Incident Count')
                 
    fig.update_traces(textfont_size=14, textposition="outside", cliponaxis=False)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', 
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#fff',
        yaxis={'categoryorder':'total ascending'},
        margin=dict(t=40, b=10, l=10, r=10),
        xaxis_title=None,
        yaxis_title=None
    )
    st.plotly_chart(fig, use_container_width=True)
